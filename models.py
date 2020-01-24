from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel
)
from wagtail.core.fields import RichTextField
from wagtail.contrib.forms.models import (
    AbstractEmailForm,
    AbstractFormField
)
from wagtail.core.blocks import URLBlock, TextBlock, StructBlock, StreamBlock, CharBlock, RichTextBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, MultiFieldPanel 
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.snippets.models import register_snippet
# Create your models here.

class CommonStreamBlock(StreamBlock):
    heading = CharBlock(classname="full title", blank=True)
    paragraph = RichTextBlock(blank=True)
    embed = EmbedBlock(blank=True)
    image = ImageChooserBlock(blank=True)
    testimonial = StructBlock([
        ('test_name', TextBlock(blank=True)),
        ('test_quote', TextBlock(blank=True)),
        ('test_pic', ImageChooserBlock(blank=True)),
    ])
    buttonLink = StructBlock([
        ('text', TextBlock(blank=True)),
        ('link', URLBlock(label="external URL", blank=True)),
    ])

    class Meta:
        icon = 'cogs'

class Seo(models.Model):
    ''' Add extra seo fields to pages such as icons. '''
    google_ad_code = models.CharField(max_length=50, null=True, blank=True)
    seo_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Optional social media image 300x300px image < 300kb."
    )

    panels = [
        MultiFieldPanel(
            [
                ImageChooserPanel('seo_image'),
                FieldPanel('google_ad_code'),
            ],
            heading="Additional SEO options ...",
        )

    ]

    class Meta:
        """Abstract Model."""

        abstract = True

@register_snippet
class Google(models.Model):
    site_tag = models.CharField(max_length=255)

    panels = [
        FieldPanel('site_tag'),
    ]

    def __str__(self):
        return "Google Site Tag : " + self.site_tag


class FormField(AbstractFormField):
    page = ParentalKey(
        'ContactPage', 
        on_delete=models.CASCADE,
        related_name='form_fields',
    )


class ContactPage(AbstractEmailForm, Seo):
    intro = StreamField(CommonStreamBlock(), null=True, blank=True,)
    thank_you_text = RichTextField(blank=True)
    css_label = 'Add CSS (FontAwesome and Bootstrap classes) '

    button_css = models.CharField(max_length=300, 
                    default='btn-success', 
                    null=True, blank=True, 
                    verbose_name= 'Button CSS',
                    help_text= 'Classes from FontAwesome and Bootstrap can be used')
    button_text = models.CharField(max_length=300, 
                    default='Submit', 
                    null=True, blank=True,
                    help_text= 'FontAwesome icons can be used')
 
    template = 'contact/contact_page.html'
    def get_context(self, request):
        context = super(ContactPage, self).get_context(request)
        context['menuitems'] = request.site.root_page.get_descendants(
            inclusive=True).live().in_menu()

        return context

    content_panels = AbstractEmailForm.content_panels + [
        StreamFieldPanel('intro'),
        InlinePanel('form_fields', label='Form Fields'),
        MultiFieldPanel([
            FieldPanel('button_css'),
            FieldPanel('button_text'),
        ], heading='Button Settings'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname='col6'),
                FieldPanel('to_address', classname='col6'),
            ]),
            FieldPanel('subject'),
        ], heading='Email Settings'),
    ]
    
    promote_panels = AbstractEmailForm.promote_panels + Seo.panels
