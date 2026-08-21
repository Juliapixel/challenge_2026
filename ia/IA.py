
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, mean_absolute_error, f1_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEATURES_PATH = os.path.join(BASE_DIR, "features", "output", "dataset_features.csv")

FEATURE_COLS = [
    "altura_cm",
    "umidade_solo_pct",
    "taxa_crescimento_recente_cm_dia",
    "dias_desde_ultima_poda",
    "chuva_acumulada_7d_mm",
    "temp_media_7d_c",
]

def split_temporal(df, col_data="data_referencia", frac_train=0.80):
    df = df.sort_values(col_data).reset_index(drop=True)
    datas_unicas = np.sort(df[col_data].unique())
    n = len(datas_unicas)
    
    corte_train = datas_unicas[int(n * frac_train)]

    train = df[df[col_data] <= corte_train]
    test = df[df[col_data] > corte_train]
    
    return train, test, corte_train


def main():
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"Arquivo de features não encontrado em: {FEATURES_PATH}")

    df = pd.read_csv(FEATURES_PATH, parse_dates=["data_referencia"])
    
    # Split 80% Treino e 20% Teste
    train, test, corte_train = split_temporal(df, frac_train=0.80)

    print(f"Split temporal: treino até {pd.Timestamp(corte_train).date()} ({len(train)} linhas), "
    f"teste depois ({len(test)} linhas)\n")

    X_train, X_test = train[FEATURE_COLS], test[FEATURE_COLS]
    #  MODELO 1: CLASSIFICAÇÃO DE RISCO 
    y_train_cls = train["risco_classe"]
    y_test_cls = test["risco_classe"]

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=8, class_weight="balanced", random_state=42
    )
    clf.fit(X_train, y_train_cls)
    pred_cls = clf.predict(X_test)

    print("=" * 60)
    print("MODELO 1: Classificação de risco por trecho")
    print("=" * 60)
    print(classification_report(y_test_cls, pred_cls, zero_division=0))
    f1_macro = f1_score(y_test_cls, pred_cls, average="macro")
    print(f"F1-macro: {f1_macro:.3f}")

    print("\nImportância das features (risco):")
    for col, imp in sorted(zip(FEATURE_COLS, clf.feature_importances_), key=lambda x: -x[1]):
        print(f"  {col}: {imp:.3f}")

    #  MODELO 2: REGRESSÃO (DIAS ATÉ A PODA) 
    y_train_reg = train["dias_ate_proxima_poda"]
    y_test_reg = test["dias_ate_proxima_poda"]

    reg = RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42)
    reg.fit(X_train, y_train_reg)
    pred_reg = reg.predict(X_test)

    mae = mean_absolute_error(y_test_reg, pred_reg)
    print("\n" + "=" * 60)
    print("MODELO 2: Dias até a próxima poda (regressão)")
    print("=" * 60)
    print(f"MAE no teste: {mae:.2f} dias")
    print(f"Média real de dias até poda no teste: {y_test_reg.mean():.1f}")
    # salva os modelos treinados
    import joblib
    models_dir = os.path.join(BASE_DIR, "models", "output")
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(clf, os.path.join(models_dir, "modelo_risco.pkl"))
    joblib.dump(reg, os.path.join(models_dir, "modelo_dias_ate_poda.pkl"))
    print(f"\nModelos salvos em {models_dir}/")

if __name__ == "__main__":
    main()