import React from 'react';

const Footer: React.FC = () => {
  return (
    <div
      style={{
        textAlign: 'center',
        padding: '20px 0',
        color: '#8A7F70',
        fontSize: 13,
      }}
    >
      Your Recipe © {new Date().getFullYear()}
    </div>
  );
};

export default Footer;
