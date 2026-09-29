class MaviloTheme {
  constructor() {
    this.bindMenu();
    this.bindQuantity();
    this.bindCartDrawer();
    this.bindCartLines();
    this.bindVariantSelection();
    this.bindProductForms();
    this.bindStickyAtc();
  }

  bindCartLines() {
    document.addEventListener('click', async (event) => {
      const quantityButton = event.target.closest('[data-cart-quantity]');
      if (quantityButton) {
        event.preventDefault();
        const input = quantityButton.closest('[data-quantity]')?.querySelector('[data-cart-line-input]');
        if (!input) return;
        const step = quantityButton.dataset.cartQuantity === 'plus' ? 1 : -1;
        const quantity = Math.max(0, Number(input.value || 0) + step);
        await this.changeCartLine(Number(input.dataset.line), quantity);
        return;
      }
      const remove = event.target.closest('[data-cart-remove]');
      if (remove) {
        event.preventDefault();
        await this.changeCartLine(Number(remove.dataset.line), 0);
      }
    });

    document.addEventListener('change', async (event) => {
      const input = event.target.closest('[data-cart-line-input]');
      if (!input) return;
      await this.changeCartLine(Number(input.dataset.line), Math.max(0, Number(input.value || 0)));
    });
  }

  async changeCartLine(line, quantity) {
    try {
      await fetch('/cart/change.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ line, quantity })
      });
    } finally {
      await this.refreshCart();
    }
  }

  bindStickyAtc() {
    document.addEventListener('click', (event) => {
      const sticky = event.target.closest('[data-sticky-add]');
      if (!sticky || sticky.hasAttribute('disabled')) return;
      const form = document.querySelector('[data-product-section] [data-product-form]');
      if (form) form.requestSubmit();
    });
  }

  bindMenu() {
    document.querySelectorAll('[data-menu-toggle]').forEach((button) => {
      const nav = document.querySelector('[data-nav]');
      button.addEventListener('click', () => {
        const expanded = button.getAttribute('aria-expanded') === 'true';
        button.setAttribute('aria-expanded', String(!expanded));
        nav?.classList.toggle('is-open');
      });
    });
  }

  bindQuantity() {
    document.addEventListener('click', (event) => {
      const button = event.target.closest('[data-quantity-button]');
      if (!button) return;
      const wrapper = button.closest('[data-quantity]');
      const input = wrapper?.querySelector('input[type="number"]');
      if (!input) return;
      const step = button.dataset.quantityButton === 'plus' ? 1 : -1;
      const min = Number(input.getAttribute('min') || 1);
      const value = Math.max(min, Number(input.value || min) + step);
      input.value = value;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
  }

  bindCartDrawer() {
    document.addEventListener('click', (event) => {
      if (event.target.closest('[data-cart-open]')) {
        event.preventDefault();
        this.openCart();
      }
      if (event.target.closest('[data-cart-close]')) this.closeCart();
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') this.closeCart();
    });
  }

  bindVariantSelection() {
    document.querySelectorAll('[data-product-section]').forEach((section) => {
      const productJson = section.querySelector('[data-product-json]');
      if (!productJson) return;

      let product;
      try {
        product = JSON.parse(productJson.textContent);
      } catch (error) {
        return;
      }

      section.addEventListener('change', (event) => {
        if (!event.target.matches('[data-option-position]')) return;
        this.updateSelectedVariant(section, product);
      });

      section.addEventListener('click', (event) => {
        const thumbnail = event.target.closest('[data-product-thumbnail]');
        if (!thumbnail) return;
        this.updateFeaturedImage(section, thumbnail.dataset.imageSrc, thumbnail.dataset.imageAlt);
      });
    });
  }

  updateSelectedVariant(section, product) {
    const selectedOptions = [];
    section.querySelectorAll('[data-option-position]:checked').forEach((input) => {
      selectedOptions[Number(input.dataset.optionPosition) - 1] = input.value;
    });

    const variant = product.variants.find((candidate) => {
      return candidate.options.every((option, index) => option === selectedOptions[index]);
    });

    this.renderVariantState(section, variant);
  }

  renderVariantState(section, variant) {
    const idInput = section.querySelector('[data-variant-id]');
    const addButton = section.querySelector('[data-add-to-cart]');
    const addText = section.querySelector('[data-add-to-cart-text]');
    const price = section.querySelector('[data-product-price]');
    const availability = section.querySelector('[data-product-availability]');

    if (!variant) {
      if (addButton) addButton.setAttribute('disabled', 'disabled');
      if (addText) addText.textContent = 'Unavailable';
      if (availability) availability.textContent = 'This option combination is unavailable';
      return;
    }

    if (idInput) idInput.value = variant.id;
    if (price) price.innerHTML = this.formatVariantPrice(section, variant);

    const stickyPrice = section.querySelector('[data-product-price-sticky]');
    const stickyButton = section.querySelector('[data-sticky-add]');
    if (stickyPrice) stickyPrice.textContent = this.formatMoney(variant.price);
    if (stickyButton) {
      stickyButton.toggleAttribute('disabled', !variant.available);
      stickyButton.textContent = variant.available ? 'Add to cart' : 'Sold out';
    }

    if (variant.available) {
      if (addButton) addButton.removeAttribute('disabled');
      if (addText) addText.textContent = 'Add to cart';
      if (availability) availability.textContent = 'In stock and ready to order';
    } else {
      if (addButton) addButton.setAttribute('disabled', 'disabled');
      if (addText) addText.textContent = 'Sold out';
      if (availability) availability.textContent = 'Currently unavailable';
    }

    if (variant.featured_image?.src) {
      this.updateFeaturedImage(section, variant.featured_image.src, variant.featured_image.alt || 'Product image');
    }

    const url = new URL(window.location.href);
    url.searchParams.set('variant', variant.id);
    window.history.replaceState({}, '', url.toString());
  }

  formatVariantPrice(section, variant) {
    const price = this.formatMoney(variant.price);
    if (variant.compare_at_price && variant.compare_at_price > variant.price) {
      return `<span class="price">${price}<s>${this.formatMoney(variant.compare_at_price)}</s></span>`;
    }
    return `<span class="price">${price}</span>`;
  }

  formatMoney(cents) {
    try {
      return new Intl.NumberFormat(document.documentElement.lang || 'en-US', {
        style: 'currency',
        currency: window.Shopify?.currency?.active || 'USD'
      }).format(cents / 100);
    } catch (error) {
      return `$${(cents / 100).toFixed(2)}`;
    }
  }

  updateFeaturedImage(section, src, alt) {
    const image = section.querySelector('[data-product-featured-image]');
    if (!image || !src) return;
    image.src = src;
    image.removeAttribute('srcset');
    image.alt = alt || image.alt;
  }

  bindProductForms() {
    document.addEventListener('submit', async (event) => {
      const form = event.target.closest('[data-product-form]');
      if (!form) return;
      if (form.dataset.ajax === 'false') return;

      event.preventDefault();
      const submit = form.querySelector('[type="submit"]');
      const wasDisabled = submit?.hasAttribute('disabled');
      submit?.setAttribute('disabled', 'disabled');

      try {
        const response = await fetch('/cart/add.js', {
          method: 'POST',
          headers: { 'Accept': 'application/json' },
          body: new FormData(form)
        });
        if (!response.ok) throw await response.json();
        await this.refreshCart();
        this.openCart();
      } catch (error) {
        const message = error?.description || error?.message || 'Unable to add item to cart.';
        this.showFormError(form, message);
      } finally {
        if (!wasDisabled) submit?.removeAttribute('disabled');
      }
    });
  }

  showFormError(form, message) {
    let error = form.querySelector('[data-form-error]');
    if (!error) {
      error = document.createElement('div');
      error.className = 'form-status';
      error.dataset.formError = '';
      form.prepend(error);
    }
    error.textContent = message;
  }

  async refreshCart() {
    const [cartResponse, sectionResponse] = await Promise.all([
      fetch('/cart.js'),
      fetch('/?section_id=cart-drawer')
    ]);
    const cart = await cartResponse.json();
    const html = await sectionResponse.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const content = doc.querySelector('[data-cart-section]');
    const target = document.querySelector('[data-cart-content]');
    if (content && target) target.innerHTML = content.innerHTML;
    document.querySelectorAll('[data-cart-count]').forEach((el) => { el.textContent = cart.item_count; });
  }

  openCart() {
    const drawer = document.querySelector('[data-cart-drawer]');
    if (!drawer) return;
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    this.refreshCart();
  }

  closeCart() {
    const drawer = document.querySelector('[data-cart-drawer]');
    if (!drawer) return;
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }
}

document.addEventListener('DOMContentLoaded', () => new MaviloTheme());
