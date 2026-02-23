import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useCookieConsent } from '../hooks/useCookieConsent';

export const SecurityBanner: React.FC = () => {
    const { isAuthenticated } = useAuth();
    const { hasConsented } = useCookieConsent();

    if (!isAuthenticated || !hasConsented) {
        return null;
    }

    return (
        <div style={{
            backgroundColor: '#fff3cd',
            border: '2px solid #ffc107',
            borderRadius: '4px',
            padding: '12px 16px',
            margin: '0 0 16px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            position: 'sticky',
            top: 0,
            zIndex: 1000,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
            <span style={{ fontSize: '24px', flexShrink: 0 }}>⚠️</span>
            <div>
                <strong style={{ color: '#856404' }}>Important Security Notice:</strong>
                <p style={{ margin: '4px 0 0 0', color: '#856404', fontSize: '14px' }}>
                    Do NOT upload personal medical files or any real personally identifiable documents.
                    This is a demonstration tool only. Use sample or mock data instead.
                </p>
            </div>
        </div>
    );
};
