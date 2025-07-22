# from sentence_transformers import SentenceTransformer
# import time
# t11 = time.time()
# model = SentenceTransformer("all-MiniLM-L6-v2")
# import numpy as np
# print("time in loading model:", time.time()- t11, " sec")



# ref_sentences = [  

#     "Is this a residential address for the Sender? (Yes/No)",
#     "Is the pickup address the same as the Sender's address? (Yes/No)",
#     "Is this a residential address for the recipient? (Yes/No)",


# ]



# ref_embeddings = model.encode(ref_sentences)


# def similarity_score(target_sentence):
#     target_embeddings = model.encode(target_sentence)
#     similarities = model.similarity(ref_embeddings, target_embeddings).tolist()
#     print(similarities)
#     return np.max(similarities)



# #print(similarity_score("is pickup address is same as senders address"))