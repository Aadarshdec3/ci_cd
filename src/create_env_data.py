import pandas as pd
import os

prod_path = "data/prod"
dev_path = "data/dev"
qa_path = "data/qa"

os.makedirs(dev_path,exist_ok=True)
os.makedirs(qa_path,exist_ok=True)

def split_fact(file_name):
    df = pd.read_csv(f"{prod_path}/{file_name}")

    #shuffle for randomness
    df =df.sample(frac=1,random_state=42).reset_index(drop=True)

    total_rows = len(df)

    dev_data = int(total_rows * 0.20)
    qa_data = dev_data+int(total_rows * 0.40)

    dev_df = df.iloc[:dev_data]
    qa_df = df.iloc[dev_data:qa_data]


    dev_df.to_csv(f"{dev_path}/{file_name}",index=False)
    qa_df.to_csv(f"{qa_path}/{file_name}",index=False)

    print(f"split done {file_name}")

def copy_dim(file_name):
    df = pd.read_csv(f"{prod_path}/{file_name}")

    df.to_csv(f"{dev_path}/{file_name}",index=False)
    df.to_csv(f"{qa_path}/{file_name}",index=False)

    print(f"dim table coped{file_name}")

def main():
    files = os.listdir(prod_path)

    for file in files:
        if file.lower().startswith("s"):
            split_fact(file)
        else:
            copy_dim(file)
    
    print("\n dev and qa tables are created")

if __name__ == "__main__":
    main()