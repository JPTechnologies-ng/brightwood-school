
const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.main-nav');

if (menuButton && navigation) {
  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    menuButton.setAttribute(
      'aria-label',
      isOpen ? 'Open navigation' : 'Close navigation'
    );
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
      const formData = new FormData(inquiryForm);

      // Replace this placeholder with your Web3Forms access key.
      formData.set('access_key', '64d7638e-5dc0-4e1d-bb8a-85caf108ad9c');

      formData.set('subject', 'New School Website Inquiry');

      const response = await fetch(
        'https://api.web3forms.com/submit',
        {
          method: 'POST',
          body: formData,
        }
      );

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(
          result.message || 'Unable to send your message. Please try again.'
        );
      }

      inquiryForm.reset();
      status.textContent =
        'Thanks for reaching out. We’ll be in touch soon.';

    } catch (error) {
      status.textContent =
        error.message || 'We could not send your note. Please try again.';

      status.classList.add('is-error');

    } finally {
      submitButton.disabled = false;
    }
  });
}
