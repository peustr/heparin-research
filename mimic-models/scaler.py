from sklearn.preprocessing import StandardScaler


def get_scaled_values(df_train, df_test, features, target):
    sc = StandardScaler()
    X_train = sc.fit_transform(df_train[features])
    y_train = df_train[target]
    X_test = sc.transform(df_test[features])
    y_test = df_test[target]
    return X_train, y_train, X_test, y_test
