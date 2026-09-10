import torch
import numpy as np
import torchxrayvision as xrv
import skimage
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# Load pretrained model (chest X-ray, 18 pathologies)
_model = xrv.models.DenseNet(weights="densenet121-res224-all")
_model.eval()

def detect_abnormalities(image_path: str):
    """Returns list of findings with confidence scores."""
    img = skimage.io.imread(image_path)
    img = xrv.datasets.normalize(img, 255)

    # Handle grayscale / RGB
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
        for p, c in zip(pathologies, preds) if c > 0.3
    ]
    return findings, img

def generate_heatmap(image_path: str, img_tensor):
    """Creates a Grad-CAM heatmap showing where the model looked."""
    target_layer = [_model.features[-1]]
    cam = GradCAM(model=_model, target_layers=target_layer)

    # Run forward pass to get predictions for target selection
    with torch.no_grad():
        preds = _model(img_tensor).cpu().numpy()[0]

    # Pick the highest-confidence pathology as the target
    target_class = int(preds.argmax())

    # Newer grad-cam requires targets as a list
    from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
    targets = [ClassifierOutputTarget(target_class)]

    grayscale_cam = cam(input_tensor=img_tensor, targets=targets)[0]

    raw = skimage.io.imread(image_path)
    raw = skimage.transform.resize(raw, (grayscale_cam.shape[0], grayscale_cam.shape[1]))
    raw = np.float32(raw) / 255
    if raw.ndim == 2:
        raw = np.stack([raw] * 3, axis=-1)

    heatmap = show_cam_on_image(raw, grayscale_cam, use_rgb=True)
    return heatmap