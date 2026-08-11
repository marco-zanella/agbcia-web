/** Points an <img> at a Blob, revoking the previous object URL it held. */
export function applyBlobToImg(imgEl, blob) {
  const previousUrl = imgEl.dataset.objectUrl;
  const url = URL.createObjectURL(blob);
  imgEl.src = url;
  imgEl.dataset.objectUrl = url;
  if (previousUrl) URL.revokeObjectURL(previousUrl);
  return url;
}

/** Debounces `fn`, keeping only the trailing call after `delayMs` of quiet. */
export function debounce(fn, delayMs) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delayMs);
  };
}
