import React from 'react';
import { ImageStyle } from '../../types';

interface StyleSelectorProps {
  value?: ImageStyle;
  onChange: (style: ImageStyle | undefined) => void;
}

export const StyleSelector: React.FC<StyleSelectorProps> = ({ value, onChange }) => {
  const styles = Object.values(ImageStyle);

  return (
    <div className="style-selector">
      <label htmlFor="style-select">Style (Optional):</label>
      <select
        id="style-select"
        value={value || ''}
        onChange={(e) => onChange(e.target.value as ImageStyle || undefined)}
      >
        <option value="">Auto (AI decides)</option>
        {styles.map((style) => (
          <option key={style} value={style}>
            {style.charAt(0).toUpperCase() + style.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
};
