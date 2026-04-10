# Triage-X Frontend

React-based user interface for the Triage-X ML-powered patient triage system.

## Features

- 📋 Comprehensive patient data input form
- 🎨 Color-coded severity display
- 📊 Confidence visualization
- 📱 Responsive design
- ⚡ Real-time predictions

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

The `.env` file is already configured:
```
REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm start
```

The app will open at http://localhost:3000

## Usage

1. **Fill in Patient Information**
   - Demographics (age, gender)
   - Vital signs (heart rate, BP, oxygen saturation, temperature, respiratory rate)
   - Symptoms (chest pain, fever, breathing difficulty, injury)
   - Medical history (diabetes, heart disease, hypertension, asthma)

2. **Click "Predict Triage Level"**
   - The app sends data to the backend API
   - ML model analyzes the patient data
   - Results are displayed with color-coded severity

3. **View Results**
   - Severity level (Immediate, Urgent, Moderate, Minor)
   - Confidence percentage
   - Priority code
   - Visual confidence bar

4. **New Assessment**
   - Click "New Assessment" to evaluate another patient

## Severity Levels

- 🚨 **Immediate** (Red #ff4d4d) - Requires immediate medical attention
- ⚠️ **Urgent** (Orange #ff9500) - Needs prompt medical care
- ⚡ **Moderate** (Yellow #ffd200) - Should be seen soon
- ✅ **Minor** (Green #4caf50) - Can wait for routine care

## Components

### PatientForm
- Collects all 17 patient data fields
- Validates input ranges
- Handles form submission
- Displays loading state

### ResultCard
- Shows prediction results
- Color-coded severity badge
- Confidence visualization
- Descriptive text for each severity level

### App
- Main application container
- Manages state (result, loading, error)
- Coordinates form and result display

## API Integration

The app uses Axios to communicate with the backend:

```javascript
// api.js
predictTriage(patientData) → POST /predict
checkHealth() → GET /ping
```

## Build for Production

```bash
npm run build
```

Creates optimized production build in `build/` directory.

## Environment Variables

- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Error
- Ensure backend server is running on port 8000
- Check CORS settings in backend
- Verify `.env` file has correct API URL

### Build Errors
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Clear npm cache: `npm cache clean --force`

## Development

### File Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── PatientForm.jsx
│   │   ├── PatientForm.css
│   │   ├── ResultCard.jsx
│   │   └── ResultCard.css
│   ├── api.js
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── .env
├── package.json
└── README.md
```

## License

Part of the Triage-X project.
