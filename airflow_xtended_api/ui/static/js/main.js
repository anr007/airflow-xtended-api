// after the fields have been disabled, wait for a few seconds and re-enable them for the next execution
function enableEmptyFieldsByDelay(form) {
  setTimeout(function () {
    for (let i = 0; i < form.length; i++) {
      form[i].disabled = false;
    }
  }, 2000); //2 seconds
}

// upon submission of the form, disable the empty fields so that they aren't passed as GET arguments
function disableEmptyFields(form) {
  for (let i = 0; i < form.length; i++) {
    if (form[i].value === "") {
      form[i].disabled = true;
    }
  }
  // after the fields have been disabled, pause for a few seconds and then enable them
  enableEmptyFieldsByDelay(form);
  return true;
}
