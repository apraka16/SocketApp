from haystack import indexes
from .models import Song


class SongIndex(indexes.SearchIndex, indexes.Indexable):
    # text = indexes.CharField(document=True, use_template=True)

    text = indexes.EdgeNgramField(document=True, use_template=True)
    category = indexes.CharField(model_attr='category')
    # genre = indexes.CharField(model_attr='genre')

    # content_auto = indexes.EdgeNgramField(model_attr='song_name')
    # content_auto = indexes.EdgeNgramField(model_attr='artist')

    def get_model(self):
        return Song

    def index_queryset(self, using=None):
        # Used when the entire index for the model is updated
        return self.get_model().objects.all()
