// src/components/PatientForm.jsx
import React, { useState } from "react";
import { predictSeverity } from "../api";
import ResultCard from "./ResultCard";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

toast.configure();

const initialState = {
  heart_rate: 80,
  systolic_bp: 120,
  diastolic_bp: 80,
  oxygen_saturation: 98,
  temperature: 37.0,
  respiratory_rate: 16,
  chest_pain: 0,
  fever: 0,
  breathing_difficulty: 0,
  injury_type: 0,
  diabetes: 0,
  heart_disease: 0,
  hypertension: 0,
  asthma: 0,
  age: 35,
  gender: "male",
};

export default function PatientForm() {
  const [form, setForm] = useState(initialState);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const onChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === "checkbox" ? (checked ? 1 : 0) : value;
    setForm({ ...form, [name]: val });
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await predictSeverity(form);
      const { severity, confidence } = response.data;
      setResult({ severity, confidence: Number(confidence) });

      // Immediate or Urgent → toast notification
      if (severity === "Immediate" || severity === "Urgent") {
        toast.error(`⚠️  ALERT: ${severity} case!`, {
          position: "top-right",
          autoClose: false,
        });
      } else {
        toast.success(`✔️  ${severity} case.`);
      }
    } catch (err) {
      console.error(err);
      toast.error("❌  Something went wrong. Check console.");
    } finally {
      setLoading(false);
    }
  };

  const renderSelect = (name, label, options) => (
    <div>
      <label>{label}:</label>
      <select name={name} value={form[name]} onChange={onChange}>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );

  const renderCheckbox = (name, label) => (
    <div>
      <label>
        <input
          type="checkbox"
          name={name}
          checked={form[name] === 1}
          onChange={onChange}
        />
        {label}
      </label>
    </div>
  );

  const renderNumber = (name, label, min, max, step = 1) => (
    <div>
      <label>{label}:</label>
      <input
        type="number"
        name={name}
        value={form[name]}
        min={min}
        max={max}
        step={step}
        onChange={onChange}
        required
      />
    </div>
  );

  return (
    <div className="patient-form">
      <h1>TRIAGE‑X – Smart Triage</h1>

      <form onSubmit={onSubmit}>
        <fieldset>
          <legend>Vitals</legend>
          {renderNumber("heart_rate", "Heart Rate (bpm)", 30, 250)}
          {renderNumber("systolic_bp", "Systolic BP (mmHg)", 50, 250)}
          {renderNumber("diastolic_bp", "Diastolic BP (mmHg)", 30, 150)}
          {renderNumber("oxygen_saturation", "O₂ Sat (%)", 50, 100)}
          {renderNumber("temperature", "Temp (°C)", 30, 45, 0.1)}
          {renderNumber("respiratory_rate", "Respiratory Rate", 5, 60)}
        </fieldset>

        <fieldset>
          <legend>Symptoms</legend>
          {renderCheckbox("chest_pain", "Chest Pain")}
          {renderCheckbox("fever", "Fever")}
          {renderCheckbox("breathing_difficulty", "Breathing Difficulty")}
          {renderCheckbox("injury_type", "Traumatic Injury")}
        </fieldset>

        <fieldset>
          <legend>Medical History</legend>
          {renderCheckbox("diabetes", "Diabetes")}
          {renderCheckbox("heart_disease", "Heart Disease")}
          {renderCheckbox("hypertension", "Hypertension")}
          {renderCheckbox("asthma", "Asthma")}
        </fieldset>

        <fieldset>
          <legend>Demographics</legend>
          {renderNumber("age", "Age (years)", 0, 120)}
          {renderSelect("gender", "Gender", ["male", "female", "other"])}
        </fieldset>

        <button type="submit" disabled={loading}>
          {loading ? "Scoring…" : "Predict Severity"}
        </button>
      </form>

      {result && <ResultCard severity={result.severity} confidence={result.confidence} />}
    </div>
  );
}
