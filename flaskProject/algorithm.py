import pandas as pd
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
from sklearn.metrics import pairwise_distances
import pickle
from pprint import pprint
import json


def recom1(recipeId, df, model_name):
    model = pickle.load(open(model_name, 'rb'))
    df2 = model.transform(df['RecipeIngredientParts'])
    # Make Sparse Matrix
    sparse_df = sparse.csr_matrix(df2)
    # Calculate distances bewteen vectors from sparse matrix (cosine)
    distances = pairwise_distances(sparse_df, metric='cosine')

    recommender_df = pd.DataFrame(distances,
                                  columns=df['RecipeId'],
                                  index=df['RecipeId'])

    df3=pd.concat([df[['Name', 'RecipeId']].reset_index(),recommender_df.reset_index()],axis=1)

    return df3[[recipeId, 'Name', 'RecipeId']].sort_values(by=recipeId).head(6)[1:].iloc[:, 3].values.tolist()[-1:]

def recom2(recipes, reviews, liked, disliked):
    import pandas as pd
    from surprise import Dataset, NormalPredictor, Reader, KNNBasic
    from surprise.model_selection import cross_validate

    new = pd.DataFrame([[0, i, 5] for i in liked] + [[0, i, 0] for i in disliked],
                       columns=["AuthorId", "RecipeId", "Rating"])
    new_reviews = pd.concat([reviews, new])

    reader = Reader(rating_scale=(0, 5))
    new_data = Dataset.load_from_df(new_reviews[["AuthorId", "RecipeId", "Rating"]], reader)
    new_trainset = new_data.build_full_trainset()

    # Build an algorithm, and train it.
    new_algo = KNNBasic()
    new_algo.fit(new_trainset)

    uid = 0  # id that's guaranteed to not exist
    # get a prediction for specific users and items.
    pred = [new_algo.predict(uid, iid) for iid in new_reviews['RecipeId']]
    top_iid = sorted(set([(i.iid, i.est) for i in pred if not i.details['was_impossible']]), key=lambda i: i[1])[-100:]
    top_iid = [i[0] for i in top_iid if i[1] > 4.0 and i[0] not in liked + disliked]
    return top_iid

def intersection(lst1, lst2):
    return [value for value in lst1 if value in lst2]

def recommend(recipes, reviews, liked, disliked):
    recoms1 = []
    if liked:
        recoms1 = [i for i in recom1(liked[-1], recipes, 'transformer.pkl') if i not in liked+disliked]
        print(liked[-1])
        print(recoms1)
    recoms2 = recom2(recipes, reviews, liked, disliked)
    if not recoms1:
        return recoms2[-1]
    return (recoms1 + intersection(recoms1, recoms2))[-1]


if __name__ == "__main__":
    recipes = pd.read_csv('./data/recipes10000.csv')
    reviews = pd.read_csv('./data/reviews10000.csv', usecols=["AuthorId", "RecipeId", "Rating"])
    # liked = [648]
    # disliked = [647]
    # recom = recommend(recipes, reviews, liked, disliked)

    # pprint(recom)
    # pprint(recipes[recipes['RecipeId'] == recom].to_json(orient="records"))


    il = recipes['Images']
