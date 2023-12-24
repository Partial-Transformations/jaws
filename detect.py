import pandas as pd
import joblib

def load_model_and_predict(csv_files, model_filename):
    loaded_model = joblib.load(model_filename)
    suspected_ips = pd.DataFrame(columns=['src_ip', 'dst_ip'])

    for file in csv_files:
        data = pd.read_csv(file)
        if 'label' in data.columns:
            data = data.drop('label', axis=1)
        features = data[['size', 'src_port', 'dst_port']]
        predictions = loaded_model.predict(features)
        suspected_data = data[predictions == 'chum'][['src_ip', 'dst_ip']]
        suspected_ips = pd.concat([suspected_ips, suspected_data], ignore_index=True)
    return suspected_ips

if __name__ == "__main__":
    model_filename = "./models/detection_model.joblib"
    csv_files_to_process = ["./data/unlabeled.csv"]
    suspected_ips = load_model_and_predict(csv_files_to_process, model_filename)
    print("Suspected IP Addresses:")
    print(suspected_ips)
