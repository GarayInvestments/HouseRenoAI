export default function FormField({
  label,
  name,
  type = 'text',
  value,
  onChange,
  required = false,
  error = null,
  placeholder = '',
  options = [], // For select inputs
  rows = 3, // For textarea
  disabled = false,
  className = '',
}) {
  const baseInputClasses = `w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
    error
      ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
  } ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'} ${className}`;

  const renderInput = () => {
    switch (type) {
      case 'textarea':
        return (
          <textarea
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            required={required}
            placeholder={placeholder}
            rows={rows}
            disabled={disabled}
            className={baseInputClasses}
          />
        );

      case 'select':
        return (
          <select
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            required={required}
            disabled={disabled}
            className={baseInputClasses}
          >
            <option value="">Select {label}</option>
            {options.map((option) => (
              <option
                key={typeof option === 'object' ? option.value : option}
                value={typeof option === 'object' ? option.value : option}
              >
                {typeof option === 'object' ? option.label : option}
              </option>
            ))}
          </select>
        );

      case 'date':
      case 'datetime-local':
        return (
          <input
            type={type}
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            required={required}
            disabled={disabled}
            className={baseInputClasses}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            required={required}
            placeholder={placeholder}
            disabled={disabled}
            step="any"
            className={baseInputClasses}
          />
        );

      default:
        return (
          <input
            type={type}
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            required={required}
            placeholder={placeholder}
            disabled={disabled}
            className={baseInputClasses}
          />
        );
    }
  };

  return (
    <div className="mb-4">
      <label
        htmlFor={name}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {renderInput()}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
