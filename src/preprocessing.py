import pandas as pd


def resample_data(data, time_frames):
    df = pd.DataFrame(
        {
            "Open": data.Open,
            "High": data.High,
            "Low": data.Low,
            "Close": data.Close,
            "Volume": data.Volume,
        },
        index=data.index,
    )

    resampled_data = data.copy()

    for tf in time_frames:
        suffix = f"{tf}min"
        resampled_data[f"Open_{suffix}"] = df["Open"].resample(f"{tf}min").first()
        resampled_data[f"High_{suffix}"] = df["High"].resample(f"{tf}min").max()
        resampled_data[f"Low_{suffix}"] = df["Low"].resample(f"{tf}min").min()
        resampled_data[f"Close_{suffix}"] = df["Close"].resample(f"{tf}min").last()
        resampled_data[f"Volume_{suffix}"] = df["Volume"].resample(f"{tf}min").sum()

    resampled_data = resampled_data.fillna(method="ffill")

    for tf in time_frames:
        suffix = f"{tf}min"
        resampled_data[f"Open_{suffix}"] = resampled_data[f"Open_{suffix}"].shift(
            int(tf / 5)
        )
        resampled_data[f"High_{suffix}"] = resampled_data[f"High_{suffix}"].shift(
            int(tf / 5)
        )
        resampled_data[f"Low_{suffix}"] = resampled_data[f"Low_{suffix}"].shift(
            int(tf / 5)
        )
        resampled_data[f"Close_{suffix}"] = resampled_data[f"Close_{suffix}"].shift(
            int(tf / 5)
        )
        resampled_data[f"Volume_{suffix}"] = resampled_data[f"Volume_{suffix}"].shift(
            int(tf / 5)
        )
    return resampled_data


def create_target(data, size, future_time=5):
    shift_idx = int(-1 * future_time / 5)
    data["next_price"] = data["Close"].shift(shift_idx)
    specific_value = (
        (0.0004 * data["Close"] + 0.0004 * data["next_price"]) * size / data["Close"]
    )
    data["difference"] = data["next_price"] - data["Close"]
    data["Target"] = (data["difference"] > specific_value).astype(int) - (
        data["difference"] < -specific_value
    ).astype(int)
    data = data.drop(["difference", "next_price"], axis=1)
    return data
