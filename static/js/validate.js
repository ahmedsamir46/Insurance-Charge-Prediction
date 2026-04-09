/**
 * InsureAI — Client-side form validation
 * Runs before submission; server-side is the final safety net.
 */

(() => {
    'use strict';

    /* ── Rule definitions ────────────────────────────────────────── */
    const RULES = {
        age: {
            validate(val) {
                if (val === '') return 'Age is required.';
                const n = Number(val);
                if (!Number.isFinite(n) || !Number.isInteger(n))
                    return 'Age must be a whole number.';
                if (n < 1 || n > 120)
                    return 'Age must be between 1 and 120.';
            }
        },
        bmi: {
            validate(val) {
                if (val === '') return 'BMI is required.';
                const n = Number(val);
                if (!Number.isFinite(n)) return 'BMI must be a valid number.';
                if (n <= 0 || n > 100)   return 'BMI must be between 1 and 100.';
            }
        },
        ch: {
            validate(val) {
                if (val === '') return 'Number of children is required.';
                const n = Number(val);
                if (!Number.isFinite(n) || !Number.isInteger(n))
                    return 'Children must be a whole number.';
                if (n < 0 || n > 20)
                    return 'Children must be between 0 and 20.';
            }
        }
    };

    /* ── Helpers ─────────────────────────────────────────────────── */

    /** Show an error message below a field */
    function setError(fieldId, message) {
        const input = document.getElementById(fieldId);
        const group = input.closest('.form-group');
        const errEl = group.querySelector('.error-msg');

        input.classList.add('field-error');
        input.setAttribute('aria-invalid', 'true');
        if (errEl) {
            errEl.textContent = message;
            errEl.removeAttribute('hidden');
        }
    }

    /** Clear error state on a field (optionally mark as valid) */
    function clearError(fieldId, markValid = false) {
        const input = document.getElementById(fieldId);
        if (!input) return;
        const group = input.closest('.form-group');
        const errEl = group && group.querySelector('.error-msg');

        input.classList.remove('field-error');
        input.removeAttribute('aria-invalid');
        if (markValid) input.classList.add('field-valid');
        if (errEl) {
            errEl.textContent = '';
            errEl.setAttribute('hidden', '');
        }
    }

    /** Set error on a radio/select group (uses data-group attribute) */
    function setGroupError(groupId, message) {
        const group = document.getElementById(groupId);
        if (!group) return;
        const errEl = group.querySelector('.error-msg');
        group.classList.add('group-error');
        if (errEl) {
            errEl.textContent = message;
            errEl.removeAttribute('hidden');
        }
    }

    function clearGroupError(groupId) {
        const group = document.getElementById(groupId);
        if (!group) return;
        const errEl = group && group.querySelector('.error-msg');
        group.classList.remove('group-error');
        if (errEl) {
            errEl.textContent = '';
            errEl.setAttribute('hidden', '');
        }
    }

    /* ── Real-time validation: clear errors as user types/selects ── */
    function attachRealTime() {
        // Text / number inputs
        Object.keys(RULES).forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            el.addEventListener('input', () => {
                el.classList.remove('field-valid');   // reset green on typing
                const err = RULES[id].validate(el.value.trim());
                if (err) setError(id, err);
                else     clearError(id);
            });
            el.addEventListener('blur', () => {
                const err = RULES[id].validate(el.value.trim());
                if (err) setError(id, err);
                else     clearError(id, true);         // green ring on valid blur
            });
        });

        // Radios — clear on any selection within the group
        ['gens-group', 'smoker-group'].forEach(groupId => {
            const group = document.getElementById(groupId);
            if (!group) return;
            group.querySelectorAll('input[type="radio"]').forEach(radio => {
                radio.addEventListener('change', () => clearGroupError(groupId));
            });
        });

        // Regions select
        const regionSelect = document.getElementById('regions');
        if (regionSelect) {
            regionSelect.addEventListener('change', () => {
                const group = regionSelect.closest('.form-group');
                const errEl = group && group.querySelector('.error-msg');
                regionSelect.classList.remove('field-error');
                regionSelect.removeAttribute('aria-invalid');
                if (errEl) { errEl.textContent = ''; errEl.setAttribute('hidden', ''); }
            });
        }
    }

    /* ── Full validation on submit ───────────────────────────────── */
    function validateAll() {
        let valid = true;

        // Numeric inputs
        Object.keys(RULES).forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const err = RULES[id].validate(el.value.trim());
            if (err) { setError(id, err); valid = false; }
            else       clearError(id);
        });

        // Sex radio
        const sexChecked = document.querySelector('input[name="gens"]:checked');
        if (!sexChecked) {
            setGroupError('gens-group', 'Please select a sex.');
            valid = false;
        } else {
            clearGroupError('gens-group');
        }

        // Smoker radio
        const smokerChecked = document.querySelector('input[name="smoker"]:checked');
        if (!smokerChecked) {
            setGroupError('smoker-group', 'Please select smoker status.');
            valid = false;
        } else {
            clearGroupError('smoker-group');
        }

        // Region select
        const regionSelect  = document.getElementById('regions');
        const regionGroup   = regionSelect && regionSelect.closest('.form-group');
        const regionErr     = regionGroup && regionGroup.querySelector('.error-msg');
        if (!regionSelect || !regionSelect.value) {
            if (regionSelect) {
                regionSelect.classList.add('field-error');
                regionSelect.setAttribute('aria-invalid', 'true');
            }
            if (regionErr) { regionErr.textContent = 'Please select a region.'; regionErr.removeAttribute('hidden'); }
            valid = false;
        } else {
            if (regionSelect) {
                regionSelect.classList.remove('field-error');
                regionSelect.removeAttribute('aria-invalid');
            }
            if (regionErr) { regionErr.textContent = ''; regionErr.setAttribute('hidden', ''); }
        }

        return valid;
    }

    /* ── Scroll to the first error ───────────────────────────────── */
    function scrollToFirstError() {
        const first = document.querySelector('.field-error, .group-error input');
        if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /* ── Bootstrap ───────────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', () => {
        const form  = document.getElementById('predict-form');
        const btn   = document.getElementById('submit-btn');
        if (!form) return;

        attachRealTime();

        form.addEventListener('submit', e => {
            e.preventDefault();           // always intercept first

            const ok = validateAll();

            if (!ok) {
                scrollToFirstError();
                return;                   // block submission
            }

            // All good → show loading state and submit
            btn.textContent = 'Calculating…';
            btn.disabled    = true;
            btn.style.opacity = '0.7';
            form.submit();
        });
    });

})();
