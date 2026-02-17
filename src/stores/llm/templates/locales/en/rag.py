# for prompt ( system , documents(chunks) , footer )
from string import Template
system_prompt=Template("\n".join([# to join list element in one string (i don't know why not use traditional string)
"You are an assistant to generate a response for the user.",
"You will be provided by a set of docuemnts associated with the user's query.",
"You have to generate a response based on the documents provided.",
])) # using Template for substitution

document_prompt = Template("\n".join([
"## Document No: $doc_num",
"### Content: $chunck_text",
]
))

footer_prompt = Template("\n".join([
    "Based only on the above documents, please generate an answer for the user.",
    "## question :",
    "$query",
    ""
    "## Answer:",
]))