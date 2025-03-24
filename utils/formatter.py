class Formatter:
    @staticmethod
    def currency(value):
        return (f"R$ {float(value):,.2f}"
            .replace(",", "v")
            .replace(".", ",")
            .replace("v", ".")
        )
