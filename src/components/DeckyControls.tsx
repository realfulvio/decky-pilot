import { ButtonItem, DropdownItem, Focusable, PanelSection, PanelSectionRow, TextField, ToggleField } from '@decky/ui';
import type { Controls } from './controls';
export const deckyControls: Controls = {
  Group: ({children,className,direction='vertical'}) => <Focusable className={className} flow-children={direction}>{children}</Focusable>,
  Button: ({children, onClick, disabled}) => <PanelSectionRow><ButtonItem layout="below" onClick={onClick} disabled={disabled}>{children}</ButtonItem></PanelSectionRow>,
  Input: ({label, value, onChange, secret}) => <PanelSectionRow><TextField label={label} value={value} bIsPassword={secret} onChange={e => onChange(e.target.value)} /></PanelSectionRow>,
  Toggle: ({label, checked, onChange}) => <PanelSectionRow><ToggleField label={label} checked={checked} onChange={onChange} /></PanelSectionRow>,
  Select: ({label, value, options, onChange}) => <PanelSectionRow><DropdownItem label={label} selectedOption={value} rgOptions={options.map(o => ({data: o.value, label: o.label}))} onChange={o => onChange(String(o.data))} /></PanelSectionRow>,
  Section: ({title, children}) => <PanelSection title={title}>{children}</PanelSection>
};
