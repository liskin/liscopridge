import textwrap

import pytest  # type: ignore [import]

from liscopridge.app import reddit


@pytest.mark.vcr
def test_subreddit_atom_minscore():
    assert reddit.subreddit_atom_minscore('thinkpad', 300) == textwrap.dedent("""
        <?xml version='1.0' encoding='UTF-8'?>
        <feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
          <category term="thinkpad" label="r/thinkpad"/>
          <updated>2022-02-03T16:18:22+00:00</updated>
          <icon>https://www.redditstatic.com/icon.png/</icon>
          <id>/r/thinkpad/top/.rss?limit=100&amp;sort=top&amp;t=week</id>
          <link rel="self" href="https://www.reddit.com/r/thinkpad/top/.rss?limit=100&amp;sort=top&amp;t=week" type="application/atom+xml"/>
          <link rel="alternate" href="https://www.reddit.com/r/thinkpad/top/?limit=100&amp;sort=top&amp;t=week" type="text/html"/>
          <subtitle>IBM and Lenovo ThinkPad laptop enthusiasts!</subtitle>
          <title>top scoring links : thinkpad</title>
          <entry>
            <author>
              <name>/u/KasaneTeto_</name>
              <uri>https://www.reddit.com/user/KasaneTeto_</uri>
            </author>
            <category term="thinkpad" label="r/thinkpad"/>
            <content type="html">&lt;table&gt; &lt;tr&gt;&lt;td&gt; &lt;a href="https://www.reddit.com/r/thinkpad/comments/shueto/_/"&gt; &lt;img src="https://external-preview.redd.it/-XnT_QOg_xRjL0ExwxMehUbcpxqatMTrFROnHIzeqrg.png?width=640&amp;amp;crop=smart&amp;amp;auto=webp&amp;amp;s=81cbc8b066e051688cfb83003aebee8dc4048055" alt="." title="." /&gt; &lt;/a&gt; &lt;/td&gt;&lt;td&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/KasaneTeto_"&gt; /u/KasaneTeto_ &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://v.redd.it/cqjfu406z7f81"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/thinkpad/comments/shueto/_/"&gt;[comments]&lt;/a&gt;&lt;/span&gt; &lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;</content>
            <id>t3_shueto</id>
            <media:thumbnail url="https://external-preview.redd.it/-XnT_QOg_xRjL0ExwxMehUbcpxqatMTrFROnHIzeqrg.png?width=640&amp;crop=smart&amp;auto=webp&amp;s=81cbc8b066e051688cfb83003aebee8dc4048055"/>
            <link href="https://www.reddit.com/r/thinkpad/comments/shueto/_/"/>
            <updated>2022-02-01T13:00:44+00:00</updated>
            <published>2022-02-01T13:00:44+00:00</published>
            <title>.</title>
          </entry>
          <entry>
            <author>
              <name>/u/Rocketkt69</name>
              <uri>https://www.reddit.com/user/Rocketkt69</uri>
            </author>
            <category term="thinkpad" label="r/thinkpad"/>
            <content type="html">&lt;table&gt; &lt;tr&gt;&lt;td&gt; &lt;a href="https://www.reddit.com/r/thinkpad/comments/sfef2f/the_fact_that_the_x230_can_play_csgo_at_60fps_on/"&gt; &lt;img src="https://preview.redd.it/g6szryspgle81.jpg?width=640&amp;amp;crop=smart&amp;amp;auto=webp&amp;amp;s=e4256143f2a5fcb06e3157adab182b4efce9a3d0" alt="The fact that the x230 can play CS:GO at 60fps on decent settings is almost disgusting. Long live the x230." title="The fact that the x230 can play CS:GO at 60fps on decent settings is almost disgusting. Long live the x230." /&gt; &lt;/a&gt; &lt;/td&gt;&lt;td&gt; &amp;#32; submitted by &amp;#32; &lt;a href="https://www.reddit.com/user/Rocketkt69"&gt; /u/Rocketkt69 &lt;/a&gt; &lt;br/&gt; &lt;span&gt;&lt;a href="https://i.redd.it/g6szryspgle81.jpg"&gt;[link]&lt;/a&gt;&lt;/span&gt; &amp;#32; &lt;span&gt;&lt;a href="https://www.reddit.com/r/thinkpad/comments/sfef2f/the_fact_that_the_x230_can_play_csgo_at_60fps_on/"&gt;[comments]&lt;/a&gt;&lt;/span&gt; &lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;</content>
            <id>t3_sfef2f</id>
            <media:thumbnail url="https://preview.redd.it/g6szryspgle81.jpg?width=640&amp;crop=smart&amp;auto=webp&amp;s=e4256143f2a5fcb06e3157adab182b4efce9a3d0"/>
            <link href="https://www.reddit.com/r/thinkpad/comments/sfef2f/the_fact_that_the_x230_can_play_csgo_at_60fps_on/"/>
            <updated>2022-01-29T09:17:34+00:00</updated>
            <published>2022-01-29T09:17:34+00:00</published>
            <title>The fact that the x230 can play CS:GO at 60fps on decent settings is almost disgusting. Long live the x230.</title>
          </entry>
          </feed>
    """).strip("\n").encode('UTF-8')  # noqa: E501
