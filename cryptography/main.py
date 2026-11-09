import jwt


def main():
    encoded_jwt = jwt.encode({"some": "payload"}, "lasjdlkjasldkfjladskjflkasdjflaksdjflkasjflasdf", algorithm="HS256")
    print(encoded_jwt)
    decoded_jwt = jwt.decode(encoded_jwt, "lasjdlkjasldkfjladskjflkasdjflaksdjflkasjflasdf", algorithms=["HS256"])
    print(decoded_jwt)


if __name__ == "__main__":
    main()
