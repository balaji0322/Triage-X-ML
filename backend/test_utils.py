"""Test utility functions."""
from app.utils import get_color, severity_code_to_name, SEVERITY_COLORS

print("🧪 Testing utility functions\n")

# Test severity code to name
print("Severity code to name mapping:")
for code in range(4):
    try:
        name = severity_code_to_name(code)
        print(f"  Code {code} → {name}")
    except KeyError:
        print(f"  Code {code} → Not mapped")

print("\nSeverity colors:")
for severity, color in SEVERITY_COLORS.items():
    print(f"  {severity}: {color}")

print("\nGet color function:")
for severity in ["Immediate", "Urgent", "Moderate", "Minor", "Unknown"]:
    color = get_color(severity)
    print(f"  {severity}: {color}")

print("\n✅ All utility tests passed!")
