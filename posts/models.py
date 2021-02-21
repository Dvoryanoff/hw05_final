from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Краткое название группы'
    )
    slug = models.SlugField(
        unique=True,
        max_length=40,
        verbose_name='Слаг',
        help_text='По-английски желаемый слаг'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Про что группа?'
    )

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(
        verbose_name='Текст',
        help_text='Здесь следует ввести текст не более 2000 знаков',
        max_length=2000)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group,
                              verbose_name='Группа',
                              help_text='Выберите группу',
                              on_delete=models.SET_NULL,
                              related_name='posts', blank=True,
                              null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    @property
    def short_text(self):
        if len(self.text.__str__()) > 100:
            return f'{self.text[:97]}...'

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')

    text = models.TextField(
        help_text='Здесь следует ввести текст комментария'
    )

    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created']


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='following_unique')
        ]
