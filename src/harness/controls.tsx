import type { Controls } from '../components/controls';
export const harnessControls: Controls = {
  Button: ({children, onClick, disabled}) => <button onClick={onClick} disabled={disabled}>{children}</button>,
  Input: ({label, value, onChange, secret}) => <label>{label}<input value={value} type={secret ? 'password' : 'text'} onChange={e => onChange(e.target.value)} /></label>,
  Toggle: ({label, checked, onChange}) => <label className="toggle"><input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />{label}</label>,
  Select: ({label, value, options, onChange}) => <label>{label}<select value={value} onChange={e => onChange(e.target.value)}>{options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}</select></label>,
  Section: ({title, children}) => <section><h2>{title}</h2>{children}</section>
};
