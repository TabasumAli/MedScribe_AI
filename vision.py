import os
import torch
import torch.nn as nn
import numpy as np
import skimage
import torchvision.models as models
import torchvision.transforms as transforms
import torchxrayvision as xrv
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget


USE_CUSTOM_MODEL = True  # True = ResNet18 (2-class), False = DenseNet (18-class)

CUSTOM_MODEL_PATH = "models/medscribe_model_a_resnet18.pth"
CUSTOM_CLASS_NAMES = ["NORMAL", "PNEUMONIA"]  # index 0 = NORMAL, index 1 = PNEUMONIA

CUSTOM_IMG_SIZE = 224
CUSTOM_TRANSFORMS = transforms.Compose(
    [
        transforms.Resize((CUSTOM_IMG_SIZE, CUSTOM_IMG_SIZE)),
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)



#  MODEL LOADING

# def _load_custom_model():
#     """Load fine-tuned ResNet18 (2 classes: NORMAL, PNEUMONIA)."""
#     model = models.resnet18(weights=None)
#     model.fc = nn.Linear(model.fc.in_features, len(CUSTOM_CLASS_NAMES))
#     state = torch.load(CUSTOM_MODEL_PATH, map_location="cpu")
#     model.load_state_dict(state)
#     model.eval()
#     return model


def _load_custom_model():
    """Load fine-tuned ResNet18 from Hugging Face Hub."""
    from huggingface_hub import hf_hub_download
    from settings import HF_MODEL_REPO, HF_MODEL_FILENAME
    
    model_path = hf_hub_download(
        repo_id=HF_MODEL_REPO,
        filename=HF_MODEL_FILENAME,
    )
    
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CUSTOM_CLASS_NAMES))
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
    return model

def _load_densenet_model():
    """Load pretrained DenseNet121 from TorchXRayVision (18 pathologies)."""
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    model.eval()
    return model


if USE_CUSTOM_MODEL:
    print("🔵 Loading CUSTOM ResNet18 model...")
    _model = _load_custom_model()
    _model_type = "resnet18"
else:
    print("🟢 Loading TorchXRayVision DenseNet121 model...")
    _model = _load_densenet_model()
    _model_type = "densenet"


#  DETECTION — unified interface
def _detect_custom(image_path: str):
    """ResNet18 detection — returns NORMAL or PNEUMONIA."""
    image = Image.open(image_path).convert("RGB")
    tensor = CUSTOM_TRANSFORMS(image).unsqueeze(0)
    with torch.no_grad():
        logits = _model(tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
    findings = [
        {"label": CUSTOM_CLASS_NAMES[i], "confidence": float(round(probs[i], 3))}
        for i in range(len(CUSTOM_CLASS_NAMES))
    ]
    return findings, tensor


def _detect_densenet(image_path: str):
    """DenseNet detection — 18 pathologies."""
    img = skimage.io.imread(image_path)
    img = xrv.datasets.normalize(img, 255)
    if len(img.shape) == 3:
        img = img.mean(axis=2)
    img = img[None, ...]
    transform = xrv.datasets.XRayCenterCrop()
    img = transform(img)
    img = torch.from_numpy(img).unsqueeze(0).float()
    with torch.no_grad():
        preds = _model(img).cpu().numpy()[0]
    pathologies = _model.pathologies
    findings = [
        {"label": p, "confidence": float(round(c, 3))}
        for p, c in zip(pathologies, preds)
        if c > 0.3
    ]
    return findings, img


def detect_abnormalities(image_path: str):
    """Unified detection — routes to active model."""
    if _model_type == "resnet18":
        return _detect_custom(image_path)
    return _detect_densenet(image_path)


#  HEATMAP — unified
def _heatmap_custom(image_path: str, img_tensor):
    """Grad-CAM for ResNet18 — target layer = layer4[-1]."""
    target_layer = [_model.layer4[-1]]
    cam = GradCAM(model=_model, target_layers=target_layer)
    with torch.no_grad():
        logits = _model(img_tensor)
    target_class = int(logits.argmax(dim=1).item())
    targets = [ClassifierOutputTarget(target_class)]
    grayscale_cam = cam(input_tensor=img_tensor, targets=targets)[0]

    raw = skimage.io.imread(image_path)
    raw = skimage.transform.resize(
        raw, (grayscale_cam.shape[0], grayscale_cam.shape[1])
    )
    raw = np.float32(raw) / 255
    if raw.ndim == 2:
        raw = np.stack([raw] * 3, axis=-1)
    elif raw.shape[-1] == 4:
        raw = raw[..., :3]
    return show_cam_on_image(raw, grayscale_cam, use_rgb=True)


def _heatmap_densenet(image_path: str, img_tensor):
    """Grad-CAM for DenseNet121."""
    target_layer = [_model.features[-1]]
    cam = GradCAM(model=_model, target_layers=target_layer)
    with torch.no_grad():
        preds = _model(img_tensor).cpu().numpy()[0]
    target_class = int(preds.argmax())
    targets = [ClassifierOutputTarget(target_class)]
    grayscale_cam = cam(input_tensor=img_tensor, targets=targets)[0]

    raw = skimage.io.imread(image_path)
    raw = skimage.transform.resize(
        raw, (grayscale_cam.shape[0], grayscale_cam.shape[1])
    )
    raw = np.float32(raw) / 255
    if raw.ndim == 2:
        raw = np.stack([raw] * 3, axis=-1)
    return show_cam_on_image(raw, grayscale_cam, use_rgb=True)


def generate_heatmap(image_path: str, img_tensor):
    """Unified heatmap — routes to active model."""
    if _model_type == "resnet18":
        return _heatmap_custom(image_path, img_tensor)
    return _heatmap_densenet(image_path, img_tensor)
