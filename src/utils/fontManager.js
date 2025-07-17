// Centralised font management utility
// -------------------------------------------------
// This module centralises all font-related definitions so that the rest of the
// codebase can consume a single source of truth.  Import `fonts` anywhere you
// need to access the catalogue or `getFontStyle` to build inline styles.
// -------------------------------------------------

export const DEFAULT_FONT_SIZE = 30 // px – the project now uses a fixed 30 px size

// Catalogue of available fonts & their CSS fall-backs.  Add new entries here
// to automatically expose them throughout the application.
export const fonts = [
  { name: 'Arial',            style: 'Arial, Helvetica, sans-serif' },
  { name: 'Inter',            style: 'Inter, sans-serif' },
  { name: 'Georgia',          style: 'Georgia, serif' },
  { name: 'Helvetica',        style: 'Helvetica, Arial, sans-serif' },
  { name: 'Times New Roman',  style: 'Times New Roman, Times, serif' },
  { name: 'Verdana',          style: 'Verdana, Geneva, sans-serif' },
  { name: 'Comic Sans MS',    style: 'Comic Sans MS, cursive, sans-serif' },
  { name: 'Impact',           style: 'Impact, Charcoal, sans-serif' },
  { name: 'Palatino',         style: 'Palatino, Palatino Linotype, serif' },
  { name: 'Courier New',      style: 'Courier New, Courier, monospace' },
  { name: 'Lucida Console',   style: 'Lucida Console, Monaco, monospace' },
  { name: 'Tahoma',           style: 'Tahoma, Geneva, sans-serif' },
  // Newly added Google-hosted fonts (fully compliant & widely supported)
  { name: 'Roboto',           style: 'Roboto, Helvetica, Arial, sans-serif' },
  { name: 'Open Sans',        style: 'Open Sans, Helvetica, Arial, sans-serif' },
  { name: 'Montserrat',       style: 'Montserrat, Helvetica, Arial, sans-serif' },
  { name: 'Lato',             style: 'Lato, Helvetica, Arial, sans-serif' },
  // Additional fonts for phone case text overlays
  { name: 'Poppins',          style: 'Poppins, Helvetica, Arial, sans-serif' },
  { name: 'Nunito',           style: 'Nunito, Helvetica, Arial, sans-serif' },
  { name: 'Quicksand',        style: 'Quicksand, Helvetica, Arial, sans-serif' },
  { name: 'Pacifico',         style: 'Pacifico, cursive, sans-serif' },
  { name: 'Dancing Script',   style: 'Dancing Script, cursive, sans-serif' },
  { name: 'Bebas Neue',       style: 'Bebas Neue, Impact, Charcoal, sans-serif' },
  { name: 'Oswald',           style: 'Oswald, Impact, Charcoal, sans-serif' },
  { name: 'Playfair Display', style: 'Playfair Display, Georgia, serif' },
  { name: 'Source Sans Pro',  style: 'Source Sans Pro, Helvetica, Arial, sans-serif' },
  { name: 'Ubuntu',           style: 'Ubuntu, Helvetica, Arial, sans-serif' },
  { name: 'Raleway',          style: 'Raleway, Helvetica, Arial, sans-serif' }
]

// Helper to build a style object for the provided font & optional overrides.
export const getFontStyle = ({
  fontName = 'Arial',
  fontSize = DEFAULT_FONT_SIZE,
  color,
  additionalStyles = {}
} = {}) => {
  const font = fonts.find((f) => f.name === fontName)
  return {
    fontFamily: font ? font.style : 'Arial, sans-serif',
    fontSize: `${fontSize}px`,
    fontWeight: '500',
    lineHeight: '1.2',
    whiteSpace: 'nowrap',
    ...(color ? { color } : {}),
    ...additionalStyles
  }
} 