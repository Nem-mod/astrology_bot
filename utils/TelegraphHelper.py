from aiogram.utils.i18n import gettext as _
class TelegraphHelper():

    def __init__(self):

        self.HEADER = _(
            "<p><i>A detailed analysis of your natal chart and an in-depth interpretation of your personality using "
            "artificial intelligence trained on the best practices of Western astrology. Made with <a "
            "href=\"https://t.me/astrolog_ai_bot\"> AstroBot</a>.</i></p>")

        self.TOPICS = [
            _("Strengths & Weaknesses"),
            _("Career & Realization"),
            _("Mission"),
            _("Relationships"),
            _("Harmony & Balance"),
            _("Finances"),
            _("Blog Topics"),
            _("Success Story"),
        ]

        self.TOPIC_IMAGES = [
            "sources/natal_chart/pre_generated_images/strength_0.png",
            "sources/natal_chart/pre_generated_images/career_0.png",
            "sources/natal_chart/pre_generated_images/mission_0.png",
            "sources/natal_chart/pre_generated_images/relationship_0.png",
            "sources/natal_chart/pre_generated_images/harmony_0.png",
            "sources/natal_chart/pre_generated_images/finance_0.png",
            "sources/natal_chart/pre_generated_images/blog_0.png",
            "sources/natal_chart/pre_generated_images/success_history_0.png"

        ]
        self.TOPICS_PROMPTS = [
            _("Describe 5 unique strengths of the User and 3 areas for growth that they should work on. The answer must "
             "contain no more than 1000 characters. Add emoji. The answer to this question is based on the analysis of "
             "the natal chart."),
            _("What fields of activity could the user engage in to fully realize themselves? The answer must contain no "
             "more than 1500 characters. Add emoji. The answer to this question is based on the analysis of the natal "
             "chart."),
            _("What is the User’s mission? How can the User benefit humanity? The answer must contain no more than 1500 "
             "characters. Add emoji. The answer to this question is based on the analysis of the natal chart."),
            _("With what partner can the User build harmonious relationships? The answer must contain no more than 1000 "
             "characters. Add emoji. The answer to this question is based on the analysis of the natal chart."),
            _("How can the User achieve harmony and balance in life? Highlight 5 key points. The answer must contain no "
             "more than 1000 characters. Add emoji. The answer to this question is based on the analysis of the natal "
             "chart."),
            _("How can the User achieve financial well-being? Describe one of the most suitable paths for the User. The "
             "answer must contain no more than 2000 characters. Add emoji. The answer to this question is based on the "
             "analysis of the natal chart. Give some tips for achieving financial prosperity. Give some tips for "
             "financial literacy. Consider what financial mistakes a user can make.  Advise what books to read for this "
             "purpose."),
            _("How should a user express himself on a blog?\n\n"
             "Specify Which blog topics are close to the user:\n"
             "- Personal blogs,\n"
             "- Niche blogs or professional blogs,\n"
             "- Corporate and business blogs,\n"
             "- Educational blogs,\n"
             "- Travel,\n"
             "- Fashion and Beauty,\n"
             "- Technology and Gadgets,\n"
             "- Sports and Fitness,\n"
             "- Arts and Culture.\n\n"
             "Specify What type of blog is appropriate for the user:\n"
             "- Text,\n"
             "- photo,\n"
             "- video podcasts (youtube or short videos),\n"
             "- audio podcasts,\n"
             "- microblogging (for example Twitter, but not only)\n"
             "Give Recommendations for blog promotion.\n"
             " Indicate Which social networks are better suited.\n"
             "The answer should be no more than 1500 characters. Add an emoji. The answer to this question is based on "
             "analyzing a natal chart.\n"
             ),
            _("Write the User's success story based on the data from their natal chart. The answer must contain no more "
             "than 2000 characters. Add emoji. The answer to this question is based on all previous answers.")
        ]

        self.BLOCKQUOTE_LIST = [
            _("<h3>Strengths & Weaknesses</h3>"
             "<blockquote dir=\"auto\">What sets you apart from others, what is your superpower? And what are the growth "
             "points?</blockquote>"),
            _("<h3>Career & Realization</h3>"
             "<blockquote dir=\"auto\">Areas for your realization</blockquote>"),
            _("<h3>Mission</h3>"
             "<blockquote dir=\"auto\">Areas in which you will benefit this world by realizing yourself</blockquote>"),
            _("<h3>Relationships</h3>"
             "<blockquote dir=\"auto\">Which partner can you build a harmonious relationship with?</blockquote>"),
            _("<h3>Harmony & Balance</h3>"
             "<blockquote dir=\"auto\">What will help you achieve them?</blockquote>"),
            _("<h3>Finances</h3>"
             "<blockquote dir=\"auto\">What will help you achieve financial success?</blockquote>"),
            _("<h3>Blog Topics</h3>"
             "<blockquote dir=\"auto\">Recommendations and ideas for a blog.</blockquote>"),
            _("<h3>Success Story</h3>"
             "<blockquote dir=\"auto\">Estimated life path, based on the position of the planets at the time of your birth ("
             "consider it one of the likely successful paths of life development).</blockquote>")
        ]