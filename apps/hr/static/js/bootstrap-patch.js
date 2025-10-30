// Prevent modal backdrop error by adding a patched version of the bootstrap Modal initialization
document.addEventListener('DOMContentLoaded', function() {
  // Make sure our patch is applied after Bootstrap is fully loaded
  setTimeout(function() {
    // Backup original method
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
      const originalModalInit = bootstrap.Modal.prototype._initializeBackDrop;
      
      // Patch the method that's causing the error
      bootstrap.Modal.prototype._initializeBackDrop = function() {
        try {
          if (originalModalInit) {
            return originalModalInit.call(this);
          }
        } catch (e) {
          console.warn('Modal backdrop initialization error avoided:', e);
          // Create a basic backdrop if the original method fails
          this._backdrop = document.createElement('div');
          this._backdrop.className = 'modal-backdrop fade show';
          document.body.appendChild(this._backdrop);
        }
      };
    }
  }, 200);
});
