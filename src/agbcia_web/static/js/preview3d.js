import * as THREE from './vendor/three.module.min.js';

/**
 * A spinning box mesh standing in for the real donor banner's geometry:
 * the front face carries the box-art texture, the remaining faces (and
 * any transparent areas of the box-art image) carry the shell color.
 * Both are swappable live via the returned handle.
 */
export function createBoxPreview(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio || 1);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
  camera.position.set(0, 0, 4.2);

  // Landscape proportions, matching the real Home Menu banner box shape.
  const geometry = new THREE.BoxGeometry(2.4, 1.4, 0.6);
  const shellMaterial = new THREE.MeshStandardMaterial({ color: 0xd0d0d8, roughness: 0.6 });
  const boxArtMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6 });
  // BoxGeometry material slot order: +x, -x, +y, -y, +z (front), -z.
  const mesh = new THREE.Mesh(geometry, [
    shellMaterial,
    shellMaterial,
    shellMaterial,
    shellMaterial,
    boxArtMaterial,
    shellMaterial,
  ]);
  scene.add(mesh);

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const keyLight = new THREE.DirectionalLight(0xffffff, 1.1);
  keyLight.position.set(2, 3, 4);
  scene.add(keyLight);

  // The box-art image is composited over a fill of the current shell
  // color before becoming a texture, so any transparent area of the
  // image reveals the shell color.
  const compositeCanvas = document.createElement('canvas');
  const compositeCtx = compositeCanvas.getContext('2d');
  let boxArtImage = null;
  let shellColorHex = 'd0d0d8';
  let boxArtTexture = null;

  function recompositeBoxArt() {
    if (!boxArtImage) return;
    compositeCanvas.width = boxArtImage.naturalWidth;
    compositeCanvas.height = boxArtImage.naturalHeight;
    compositeCtx.fillStyle = `#${shellColorHex}`;
    compositeCtx.fillRect(0, 0, compositeCanvas.width, compositeCanvas.height);
    compositeCtx.drawImage(boxArtImage, 0, 0);

    if (boxArtTexture) boxArtTexture.dispose();
    boxArtTexture = new THREE.CanvasTexture(compositeCanvas);
    boxArtTexture.colorSpace = THREE.SRGBColorSpace;
    boxArtMaterial.map = boxArtTexture;
    boxArtMaterial.needsUpdate = true;
  }

  function resize() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (width === 0 || height === 0) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas);
  resize();

  let animationFrame = requestAnimationFrame(function animate(time) {
    mesh.rotation.y = time * 0.0004;
    renderer.render(scene, camera);
    animationFrame = requestAnimationFrame(animate);
  });

  return {
    setBoxArtTexture(url) {
      const image = new Image();
      image.onload = () => {
        boxArtImage = image;
        recompositeBoxArt();
      };
      image.src = url;
    },
    setShellColor(hexDigits) {
      shellColorHex = hexDigits;
      shellMaterial.color.set(`#${hexDigits}`);
      recompositeBoxArt();
    },
    dispose() {
      cancelAnimationFrame(animationFrame);
      resizeObserver.disconnect();
      renderer.dispose();
      geometry.dispose();
      shellMaterial.dispose();
      boxArtMaterial.dispose();
      if (boxArtTexture) boxArtTexture.dispose();
    },
  };
}
