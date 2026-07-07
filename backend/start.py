import os
import sys
import traceback

print("=== Starting miling-backend ===")
print(f"PORT: {os.environ.get('PORT', '8000')}")

try:
    from app.main import app
    print("App imported successfully")
except Exception as e:
    print(f"!!! ERROR importing app: {e}")
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)