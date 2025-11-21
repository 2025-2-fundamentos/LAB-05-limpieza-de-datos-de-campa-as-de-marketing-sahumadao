import os
import zipfile
import pandas as pd
"""
Escriba el codigo que ejecute la accion solicitada.
"""

# pylint: disable=import-outside-toplevel


def clean_campaign_data():
    """
    En esta tarea se le pide que limpie los datos de una campaña de
    marketing realizada por un banco, la cual tiene como fin la
    recolección de datos de clientes para ofrecerls un préstamo.

    La información recolectada se encuentra en la carpeta
    files/input/ en varios archivos csv.zip comprimidos para ahorrar
    espacio en disco.

    Usted debe procesar directamente los archivos comprimidos (sin
    descomprimirlos). Se desea partir la data en tres archivos csv
    (sin comprimir): client.csv, campaign.csv y economics.csv.
    Cada archivo debe tener las columnas indicadas.

    Los tres archivos generados se almacenarán en la carpeta files/output/.

    client.csv:
    - client_id
    - age
    - job: se debe cambiar el "." por "" y el "-" por "_"
    - marital
    - education: se debe cambiar "." por "_" y "unknown" por pd.NA
    - credit_default: convertir a "yes" a 1 y cualquier otro valor a 0
    - mortage: convertir a "yes" a 1 y cualquier otro valor a 0

    campaign.csv:
    - client_id
    - number_contacts
    - contact_duration
    - previous_campaing_contacts
    - previous_outcome: cmabiar "success" por 1, y cualquier otro valor a 0
    - campaign_outcome: cambiar "yes" por 1 y cualquier otro valor a 0
    - last_contact_day: crear un valor con el formato "YYYY-MM-DD",
        combinando los campos "day" y "month" con el año 2022.

    economics.csv:
    - client_id
    - const_price_idx
    - eurobor_three_months



    """
    
    input_dir = os.path.join("files", "input")
    output_dir = os.path.join("files", "output")
    os.makedirs(output_dir, exist_ok=True)

    parts = []
    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(".zip"):
            continue
        path = os.path.join(input_dir, fname)
        with zipfile.ZipFile(path, "r") as z:
            names = z.namelist()
            if not names:
                continue
            member = names[0]
            with z.open(member) as fh:
                df_part = pd.read_csv(fh)
                parts.append(df_part)

    if not parts:
        return

    df = pd.concat(parts, ignore_index=True)


    # Client
    client = pd.DataFrame()
    client["client_id"] = range(len(df))
    client["age"] = df["age"]

    # job
    client["job"] = (
        df["job"].astype(str).str.replace(".", "", regex=False).str.replace("-", "_")
    )
    client["marital"] = df["marital"]

    # education
    education = df["education"].astype(str).str.replace(".", "_", regex=False)
    education = education.replace({"unknown": pd.NA})
    client["education"] = education

    # credit_default
    if "credit_default" in df.columns:
        s = df["credit_default"]
        if pd.api.types.is_numeric_dtype(s):
            client["credit_default"] = s.astype(int)
        else:
            client["credit_default"] = s.astype(str).map(lambda x: 1 if str(x).lower() in ("yes", "1", "true") else 0)
    elif "default" in df.columns:
        client["credit_default"] = df["default"].astype(str).map(lambda x: 1 if x.lower() == "yes" else 0)
    else:
        client["credit_default"] = 0

    # mortgage
    if "mortgage" in df.columns:
        s = df["mortgage"]
        if pd.api.types.is_numeric_dtype(s):
            client["mortgage"] = s.astype(int)
        else:
            client["mortgage"] = s.astype(str).map(lambda x: 1 if str(x).lower() in ("yes", "1", "true") else 0)
    elif "housing" in df.columns:
        client["mortgage"] = df["housing"].astype(str).map(lambda x: 1 if x.lower() == "yes" else 0)
    else:
        client["mortgage"] = 0

    # Campaign
    campaign = pd.DataFrame()
    campaign["client_id"] = range(len(df))
    # number_contacts
    if "number_contacts" in df.columns:
        campaign["number_contacts"] = df["number_contacts"]
    elif "campaign" in df.columns:
        campaign["number_contacts"] = df["campaign"]
    else:
        campaign["number_contacts"] = df.get("number_contacts")

    # contact_duration
    if "contact_duration" in df.columns:
        campaign["contact_duration"] = df["contact_duration"]
    elif "duration" in df.columns:
        campaign["contact_duration"] = df["duration"]
    else:
        campaign["contact_duration"] = df.get("contact_duration")

    # previous_campaign_contacts
    if "previous_campaign_contacts" in df.columns:
        campaign["previous_campaign_contacts"] = df["previous_campaign_contacts"]
    elif "previous" in df.columns:
        campaign["previous_campaign_contacts"] = df["previous"]
    else:
        campaign["previous_campaign_contacts"] = df.get("previous_campaign_contacts")

    # previous_outcome
    if "previous_outcome" in df.columns:
        s = df["previous_outcome"]
        if pd.api.types.is_numeric_dtype(s):
            campaign["previous_outcome"] = s.astype(int)
        else:
            def map_prev(x):
                try:
                    return int(x)
                except Exception:
                    return 1 if str(x).lower() in ("success", "yes", "1", "true") else 0

            campaign["previous_outcome"] = s.astype(str).map(map_prev)
    elif "poutcome" in df.columns:
        campaign["previous_outcome"] = df["poutcome"].astype(str).map(lambda x: 1 if x.lower() == "success" else 0)
    else:
        campaign["previous_outcome"] = 0

    # campaign_outcome
    if "campaign_outcome" in df.columns:
        s = df["campaign_outcome"]
        if pd.api.types.is_numeric_dtype(s):
            campaign["campaign_outcome"] = s.astype(int)
        else:
            campaign["campaign_outcome"] = s.astype(str).map(lambda x: 1 if str(x).lower() in ("yes", "1", "true") else 0)
    elif "y" in df.columns:
        campaign["campaign_outcome"] = df["y"].astype(str).map(lambda x: 1 if x.lower() == "yes" else 0)
    else:
        campaign["campaign_outcome"] = 0



    try:
        dates = pd.to_datetime(
            df["day"].astype(str) + " " + df["month"].astype(str) + " 2022",
            format="%d %b %Y",
            errors="coerce",
        )
    except Exception:
        dates = pd.to_datetime(
            df["day"].astype(str) + " " + df["month"].astype(str) + " 2022",
            errors="coerce",
        )

    campaign["last_contact_date"] = dates.dt.strftime("%Y-%m-%d")

    # Economics
    econ = pd.DataFrame()
    econ["client_id"] = range(len(df))

    if "cons.price.idx" in df.columns:
        econ["cons_price_idx"] = df["cons.price.idx"]
    elif "cons_price_idx" in df.columns:
        econ["cons_price_idx"] = df["cons_price_idx"]
    else:
        econ["cons_price_idx"] = df.get("cons_price_idx")

    if "euribor3m" in df.columns:
        econ["euribor_three_months"] = df["euribor3m"]
    elif "euribor_three_months" in df.columns:
        econ["euribor_three_months"] = df["euribor_three_months"]
    else:
        econ["euribor_three_months"] = df.get("euribor_three_months")

    # Save files
    client = client[["client_id", "age", "job", "marital", "education", "credit_default", "mortgage"]]
    campaign = campaign[[
        "client_id",
        "number_contacts",
        "contact_duration",
        "previous_campaign_contacts",
        "previous_outcome",
        "campaign_outcome",
        "last_contact_date",
    ]]
    econ = econ[["client_id", "cons_price_idx", "euribor_three_months"]]

    client.to_csv(os.path.join(output_dir, "client.csv"), index=False)
    campaign.to_csv(os.path.join(output_dir, "campaign.csv"), index=False)
    econ.to_csv(os.path.join(output_dir, "economics.csv"), index=False)

    return


if __name__ == "__main__":
    clean_campaign_data()
