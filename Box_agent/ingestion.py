import os

import requests
from Box_agent.box_client import BoxClient, BoxClientError

box_client = BoxClient()
VD_REF_TEXTS_FOLDER_ID = os.environ.get("VD_REF_TEXTS_FOLDER_ID")


class BoxAgent:
    def box_ingestion(self):
        extracted_texts = []
        folder = box_client.get_all_files_in_folder(VD_REF_TEXTS_FOLDER_ID)
        files = folder["entries"]

        for file in files:
            representations = box_client.get_available_representations(file["id"])
            extracted_text_allowed = filter(
                lambda x: x["representation"] == "extracted_text", representations
            )

            if extracted_text_allowed:
                url_template = box_client.get_extracted_text_representation_metadata(
                    file["id"]
                )["representations"]["entries"][0]["content"]["url_template"]
                url_template = url_template.replace("{+asset_path}", "")

                try:
                    extracted_text = requests.get(
                        "GET", url_template, headers=box_client.headers
                    )
                    requests.raise_for_status()
                except requests.RequestException as e:
                    print(
                        f"Error downloading extracted text for file {file['id']}: {e}"
                    )
                    return BoxClientError(
                        f"Failed to download extracted text for file {file['id']}"
                    )

                extracted_texts.append(extracted_text)

        # send all text extractions to llamaindex for embedding and storage in supabase
