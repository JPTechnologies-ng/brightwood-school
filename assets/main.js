const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.main-nav');

if (menuButton && navigation) {
  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'Open navigation' : 'Close navigation');
    navigation.classList.toggle('is-open', !isOpen);
  });
}

const inquiryForm = document.querySelector('.inquiry-form');

if (inquiryForm) {
  const status = inquiryForm.querySelector('.form-status');
  const submitButton = inquiryForm.querySelector('.form-submit');

  inquiryForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.textContent = 'Sending your note...';
    status.classList.remove('is-error');
    submitButton.disabled = true;

    try {
      const response = await fetch('/api/inquiries', {
        method: 'POST',
        body: new FormData(inquiryForm),
      });
      const result = await response.json();

      if (!response.ok || !result.ok) {
        throw new Error(result.error || 'Please try again in a moment.');
      }

      inquiryForm.reset();
      status.textContent = 'Thanks for reaching out. We’ll be in touch soon.';
    } catch (error) {
      status.textContent = error.message || 'We could not send your note. Please try again.';
      status.classList.add('is-error');
    } finally {
      submitButton.disabled = false;
    }
  });
}