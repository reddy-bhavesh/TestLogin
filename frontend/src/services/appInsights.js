/**
 * Azure Application Insights for Frontend Audit Logging
 * Tracks user actions in the browser and sends to Azure Log Analytics
 */
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

// Initialize Application Insights
const connectionString = import.meta.env.VITE_APP_INSIGHTS_CONNECTION_STRING || '';

let appInsights = null;

if (connectionString) {
  appInsights = new ApplicationInsights({
    config: {
      connectionString: connectionString,
      enableAutoRouteTracking: true,
      disableFetchTracking: false,
    }
  });
  appInsights.loadAppInsights();
  appInsights.trackPageView();
}

/**
 * Track an admin/user action for audit logging
 * @param {string} adminUser - Email of the user performing the action
 * @param {string} action - Action being performed (e.g., "UPDATE_USER_ROLE")
 * @param {string} targetTenant - Tenant being affected (default: "default")
 * @param {string} targetUser - User being affected (optional)
 * @param {object} details - Additional details (optional)
 */
export function trackAdminAction(adminUser, action, targetTenant = 'default', targetUser = '', details = {}) {
  if (!appInsights) {
    console.log('[AUDIT]', { Admin_User: adminUser, Action: action, Target_Tenant: targetTenant, Target_User: targetUser, ...details });
    return;
  }

  appInsights.trackEvent({
    name: 'AdminAction',
    properties: {
      Admin_User: adminUser,
      Action: action,
      Target_Tenant: targetTenant,
      Target_User: targetUser,
      Timestamp: new Date().toISOString(),
      ...details
    }
  });
}

/**
 * Track authentication events
 */
export function trackAuthEvent(email, eventType, success) {
  if (!appInsights) {
    console.log('[AUTH]', { email, eventType, success });
    return;
  }

  appInsights.trackEvent({
    name: 'AuthEvent',
    properties: {
      Admin_User: email,
      Action: eventType,
      Target_Tenant: 'default',
      Target_User: email,
      Success: success,
      Timestamp: new Date().toISOString()
    }
  });
}

/**
 * Track page views manually
 */
export function trackPageView(pageName) {
  if (!appInsights) {
    console.log('[PAGE]', pageName);
    return;
  }
  
  appInsights.trackPageView({ name: pageName });
}

export default appInsights;
