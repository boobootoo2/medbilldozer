import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

const checkConsents = () =>
    !!localStorage.getItem('disclaimer_accepted') &&
    !!localStorage.getItem('medbilldozer_consent_shown');

export const SecurityBanner: React.FC = () => {
    const { isAuthenticated } = useAuth();
    const [consentsGiven, setConsentsGiven] = useState(checkConsents);

    useEffect(() => {
        const handler = () => setConsentsGiven(checkConsents());
        window.addEventListener('medbilldozer:consent', handler);
        return () => window.removeEventListener('medbilldozer:consent', handler);
    }, []);

    if (!isAuthenticated || !consentsGiven) {
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
