import pandas as pd
import pandas_ta as pta


def _check_data_length(close, length, indicator_name):
    if len(close) < length:
        print(f"Длина данных для {indicator_name} слишком мала: {len(close)}")
        return [np.nan] * len(close)
    return None


def _get_ema(close, index, length, step=1):
    check_result = _check_data_length(close, length, "EMA")
    if check_result is not None:
        return check_result

    sampled_close = close[::step]
    sampled_index = index[::step]

    df = pd.DataFrame(
        {"data": list(sampled_index), "close": list(sampled_close)}
    ).set_index("data")
    ema_values = pta.ema(df.close, length=length)

    # Создание полного массива длины исходных данных, заполненного NaN
    full_length_ema = np.full_like(close, np.nan, dtype=np.float64)

    # Заполнение каждого 'step'-го элемента значением EMA
    full_length_ema[::step] = ema_values

    # Создание Pandas Series из массива
    ema_series = pd.Series(full_length_ema)

    # Заполнение NaN значений предыдущими не-NaN значениями
    filled_ema = ema_series.fillna(method="ffill")

    return filled_ema.values


def _get_rsi(close, index, length, step=1):
    check_result = _check_data_length(close, length, "RSI")
    if check_result is not None:
        return check_result

    sampled_close = close[::step]
    sampled_index = index[::step]

    df = pd.DataFrame(
        {"data": list(sampled_index), "close": list(sampled_close)}
    ).set_index("data")
    rsi_values = pta.rsi(df.close, length=length)

    # Создание полного массива длины исходных данных, заполненного NaN
    full_length_rsi = np.full_like(close, np.nan, dtype=np.float64)

    # Заполнение каждого 'step'-го элемента значением EMA
    full_length_rsi[::step] = rsi_values

    # Создание Pandas Series из массива
    rsi_series = pd.Series(full_length_rsi)

    # Заполнение NaN значений предыдущими не-NaN значениями
    filled_rsi = rsi_series.fillna(method="ffill")

    return filled_rsi


def _get_macd_main_line(close, index, fast, slow, signal):
    check_result = _check_data_length(close, max(fast, slow), "MACD")
    if check_result is not None:
        return check_result

    df = pd.DataFrame({"data": list(index), "close": list(close)}).set_index("data")
    return list(pta.macd(df.close, fast=fast, slow=slow, signal=signal)["MACD_12_26_9"])


def _get_macd_signal_line(close, index, fast, slow, signal):
    check_result = _check_data_length(close, max(fast, slow), "MACD Signal Line")
    if check_result is not None:
        return check_result

    df = pd.DataFrame({"data": list(index), "close": list(close)}).set_index("data")
    return list(
        pta.macd(df.close, fast=fast, slow=slow, signal=signal)["MACDs_12_26_9"]
    )


def _get_macd_hist(close, index, fast, slow, signal):
    check_result = _check_data_length(close, max(fast, slow), "MACD Histogram")
    if check_result is not None:
        return check_result

    df = pd.DataFrame({"data": list(index), "close": list(close)}).set_index("data")
    return list(
        pta.macd(df.close, fast=fast, slow=slow, signal=signal)["MACDh_12_26_9"]
    )
