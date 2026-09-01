/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        void: '#000000',
        'bone-white': '#ffffff',
        'ash-gray': '#9a9a9a',
        'silver-mist': '#bdbdbd',
        'electric-iris': '#8052ff',
        'saffron-spark': '#ffb829',
        'deep-verdant': '#15846e',
        'signal-rose': '#ff5c7a',
        'line-hairline': '#1f1f1f',
      },
      fontFamily: {
        sans: ['PPNeueMontreal', 'Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      fontSize: {
        caption: ['12px', { lineHeight: '1.5' }],
        'nav-label': ['14px', { lineHeight: '1.2', letterSpacing: '0.025em' }],
        body: ['18px', { lineHeight: '1.5', fontWeight: '200' }],
        'body-dense': ['15px', { lineHeight: '1.4', fontWeight: '400' }],
        'stat-value': ['48px', { lineHeight: '1.0', letterSpacing: '-1.68px', fontWeight: '400' }],
        'heading-2xs': ['24px', { lineHeight: '1.25', letterSpacing: '-0.48px' }],
        'heading-xs': ['27px', { lineHeight: '1.0' }],
        subheading: ['36px', { lineHeight: '1.2' }],
        'heading-sm': ['42px', { lineHeight: '1.2', letterSpacing: '-1.68px' }],
        heading: ['48px', { lineHeight: '1.1', letterSpacing: '-1.68px' }],
        'heading-lg': ['78px', { lineHeight: '1.1', letterSpacing: '-3.12px' }],
      },
      borderRadius: {
        buttons: '24px',
        panel: '16px',
        input: '12px',
      },
      maxWidth: {
        dashboard: '1440px',
      },
      width: {
        sidebar: '240px',
      },
    },
  },
  plugins: [],
}
