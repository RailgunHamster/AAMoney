from PIL import Image, ImageFont, ImageDraw


class TextToImage:
    def __init__(self, text_or_path, break_text: list[str], water_mark: str):
        self.water_mark = water_mark
        assert type(break_text) is list
        assert len(break_text) >= 2
        if type(text_or_path) is str:
            with open(text_or_path, "r", encoding="utf-8") as file:
                self.text = file.readlines()
        else:
            self.text = text_or_path
        print("text: ", self.text)

        def get_break_point(btext):
            middle = 0
            for t in self.text:
                if btext in t:
                    break
                middle = middle + 1
            else:
                middle = -1
            assert middle >= 0
            return middle

        self.texts = []
        self.break_points = list(map(lambda t: get_break_point(t), break_text))
        break_point_len = len(self.break_points)
        self.texts.append((None, self.break_points[0]))
        for i in range(break_point_len - 1):
            self.texts.append((self.break_points[i], self.break_points[i + 1]))
        self.texts.append((self.break_points[-1], None))
        print(self.texts)

    def get_text(self, i: int):
        i = self.texts[i]
        return self.text[i[0] : i[1]]

    def map_text(self, f, rge=None):
        if type(rge) is range or type(rge) is list:
            result = []
            for r in rge:
                i = self.texts[r]
                result.append(f(self.text[i[0] : i[1]]))
            return result
        return map(lambda i: f(self.text[i[0] : i[1]]), self.texts)

    def max_line(self, i=None):
        def max_line_single(txt):
            return max(map(lambda t: len(t), txt))

        if type(i) is int:
            return max_line_single(self.get_text(i))
        if type(i) is range or type(i) is list:
            return sum(self.map_text(max_line_single, i))
        else:
            return sum(self.map_text(max_line_single))

    def line_length(self, i=None):
        if type(i) is int:
            return len(self.get_text(i))
        if type(i) is range or type(i) is list:
            return max(self.map_text(len, i))
        else:
            return max(self.map_text(len))

    def to_image(self):
        max_line = self.max_line()
        line_length = self.line_length()
        print("max_line: ", max_line)
        print("line_length: ", line_length)

        font = "font.ttc"
        font_size = 30
        factor = (0.8, 1.35)
        padding = (30, 30)

        def get_size(x, y):
            return (
                int(factor[0] * font_size * x + padding[0]),
                int(factor[1] * font_size * y + padding[1]),
            )

        size = get_size(max_line, line_length)
        image = Image.new(
            "RGB",
            size,
            color=(255, 255, 255),
        )
        posTitle = get_size(0, 0)
        ImageDraw.Draw(image).text(
            posTitle,
            self.water_mark,
            (0, 0, 0),
            ImageFont.truetype(font, int(font_size * 1.5)),
        )

        def draw_text(i: int):
            start = 0
            if i > 0:
                start = self.max_line(range(i))
            middle = (line_length / 2) - (self.line_length(i) / 2)
            pos = get_size(start, middle)
            ImageDraw.Draw(image).text(
                pos,
                "".join(self.get_text(i)),
                (0, 0, 0),
                ImageFont.truetype(font, font_size),
            )

        for i in range(len(self.texts)):
            draw_text(i)
        return image


if __name__ == "__main__":
    TextToImage("output.txt", ["下面是详细过程信息", "合计"], "豆汁儿工益小组专用").to_image().save(
        "output.jpg"
    )
