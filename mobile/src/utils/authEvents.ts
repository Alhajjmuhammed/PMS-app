/**
 * Simple event emitter for auth-related events.
 * Allows api.ts (outside React tree) to signal the AuthProvider to log out.
 */

type Listener = () => void;

let unauthorizedListener: Listener | null = null;

export const authEvents = {
  onUnauthorized(listener: Listener) {
    unauthorizedListener = listener;
  },
  emitUnauthorized() {
    if (unauthorizedListener) {
      unauthorizedListener();
    }
  },
};
