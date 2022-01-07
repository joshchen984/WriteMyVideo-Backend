function listenForUpload(buttonId, labelId) {
  const button = document.getElementById(buttonId);
  const label = document.getElementById(labelId);
  button.addEventListener('change', function () {
    label.textContent = `[${this.files[0].name}]`;
  });
}
