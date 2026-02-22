import React from 'react';

const SecurityBanner = () => {
    return (
        <div style={{
            backgroundColor: '#fff3cd',
            border: '2px solid #ffc107',
            borderRadius: '4px',
            padding: '12px 16px',
            margin: '16px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
        }}>
            <span style={{ fontSize: '24px' }}>⚠️</span>
            <div>
                <strong style={{ color: '#856404' }}>Important Security Notice:</strong>
                <p style={{ margin: '4px 0 0 0', color: '#856404' }}>
                    Do NOT upload personal medical files or any real personally identifiable documents.
                    This is a demonstration tool only. Use sample or mock data instead.
                </p>
            </div>
        </div>
    );
};

export default SecurityBanner;
