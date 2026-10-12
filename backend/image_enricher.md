Image Enricher Workflow Explained
This document breaks down image_enricher.py, the second major stage of the ingestion pipeline. It explains how raw parsed text is fused with Vision LLM data and staged for GraphRAG.

1. Environment & Path Setup
Python
BASE_DIR = os.getcwd()
PARSE_DIR = os.path.join(BASE_DIR,'parsed_files')
GRAPH_RAG = os.path.join(BASE_DIR,'graph_rag_pipeline','input')
PARSE_DIR: Defines the source directory where MinerU extracted the full.md and raw .jpg diagrams.

GRAPH_RAG: Defines the final destination directory. This confirms the ultimate goal of the script is to place the enriched files into graph_rag_pipeline/input so the knowledge graph can ingest them.

2. Image Detection (Regex)
Python
def find_images(self,markdown_text):
    image_pattern = r'!\[\]\((.*?\.jpg)\)'
    images = re.findall(image_pattern, markdown_text)
    return images
Uses Regular Expressions (re) to scan the raw full.md text from MinerU.

It hunts for standard Markdown image tags (e.g., ![](images/diagram.jpg)) and extracts the file path for every diagram the parser found.

3. Vision LLM Processing
Python
def analyze_image(self,image_path):
    # ... prompt definition ...
    with open(image_path, "rb") as f1:
        image_bytes = f1.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    response = ollama.chat(
        model="qwen2.5vl:7b",
        messages=[message],
        options={"num_ctx": 32768}
    )
    description = response['message']['content']
    
    return f"### AI Image Interpretation\nImage source: {image_path}\n{description}"
Opens the isolated diagram and converts it into a base64 string (how AI models "see" images via API).

Sends the image and a highly specific engineering prompt to a locally hosted Ollama Vision model (qwen2.5vl:7b).

Expands the context window to 32768 tokens to handle complex technical descriptions.

Returns a formatted text block containing the AI's interpretation of the thermal power plant diagram.

4. Markdown Injection
Python
def enrich_markdown(self):
    # ... loads text and finds images ...
    for index, image_path in enumerate(images,1):
        description = self.analyze_image(full_image_path)
        
        image_markdown = f"![]({image_path})"
        enriched_content = image_markdown + "\n\n" + description
        markdown_text = markdown_text.replace(image_markdown, enriched_content)

    output_path = os.path.join(document_folder,"enriched.md")
    with open(output_path,'w',encoding="utf-8") as f2 :
        f2.write(markdown_text)
Loops through every image found in the document.

Calls the analyze_image function to get the text description.

Finds the original empty image tag in the markdown and replaces it with the tag plus the new AI description.

Saves this combined, multimodal document as a new file named enriched.md inside the document's parsed folder.

5. The "Time Skip" Mechanism
Python
def start(self) :
    if os.path.exists(os.path.join(self.file_path,"enriched.md")) :
        print("Enriched markdown already exists. Skipping.")
        return
    elif self.filename + '.md' in os.listdir(GRAPH_RAG) :
        return
    
    self.enrich_markdown()
Checkpoint 1: If enriched.md already exists in the parsed_files folder, it skips processing to save time.

Checkpoint 2: If the final .md file is already sitting in the graph_rag_pipeline/input folder, it halts completely. This allows the pipeline to instantly skip hours of processing if pre-computed data is supplied.

6. Staging for GraphRAG
Python
def write_to_enriched_folder() :
    for filename in os.listdir(PARSE_DIR) :
        file_path = os.path.join(PARSE_DIR,filename)
        if os.path.exists(os.path.join(file_path,"enriched.md")) :
            # Copy enriched.md to GraphRAG input
        else :
            # Copy full.md (if no images were found) to GraphRAG input
Iterates through every folder in parsed_files.

It copies the enriched.md (or the original full.md if the document had no pictures) and pastes it directly into graph_rag_pipeline/input/.

It renames the file to match the original document name (e.g., ash_handling.md), formatting it perfectly for the next phase of the architecture.