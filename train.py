import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train_and_detect_exfiltration(csv_files):
    combined_data = pd.DataFrame()

    for file in csv_files:
        data = pd.read_csv(file)
        combined_data = pd.concat([combined_data, data], ignore_index=True)

    features = combined_data[['size', 'src_port', 'dst_port']]
    labels = combined_data['label']
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    suspected_ips = combined_data.loc[y_test[y_pred == 'chum'].index, ['src_ip', 'dst_ip']]
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    model_filename = "./models/detection_model.joblib"
    joblib.dump(model, model_filename)
    print(f"Trained model saved to: {model_filename}")

if __name__ == "__main__":
    csv_files = ["./packets_base_500k.csv", "./packets_exfil_500k.csv"]
    train_and_detect_exfiltration(csv_files)

