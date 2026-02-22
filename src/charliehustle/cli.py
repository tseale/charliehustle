"""Command-line interface for charliehustle."""

import logging
import sys
from pathlib import Path

import click
import pandas as pd

from charliehustle.config import Config


@click.group()
@click.option(
    "--data-dir", type=click.Path(), default="data", help="Data directory"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, data_dir: str, verbose: bool) -> None:
    """charliehustle -- MLB game prediction and betting simulation."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config(data_dir=Path(data_dir))


@cli.command()
@click.argument("seasons", nargs=-1, type=int, required=True)
@click.pass_context
def build(ctx: click.Context, seasons: tuple[int, ...]) -> None:
    """Fetch game data and build feature matrices.

    Example: charliehustle build 2023 2024
    """
    from charliehustle.data.features import build_feature_matrix
    from charliehustle.data.sources import fetch_season_games
    from charliehustle.data.storage import save_parquet

    config = ctx.obj["config"]

    for season in seasons:
        click.echo(f"\n--- {season} Season ---")
        games = fetch_season_games(season, config)
        features = build_feature_matrix(games, config)

        out_path = config.data_dir / f"{season}" / "features.parquet"
        save_parquet(features, out_path)
        click.echo(f"Saved {len(features)} game features to {out_path}")


@cli.command()
@click.argument("train_seasons", nargs=-1, type=int, required=True)
@click.option(
    "--model-name", default="xgb_model.pkl", help="Model filename"
)
@click.pass_context
def train(
    ctx: click.Context, train_seasons: tuple[int, ...], model_name: str
) -> None:
    """Train a model on one or more seasons.

    Example: charliehustle train 2019 2020 2021 2022 2023
    """
    from charliehustle.data.storage import load_parquet
    from charliehustle.models.train import train_model

    config = ctx.obj["config"]
    model_path = config.data_dir / "models" / model_name

    all_features = []
    for season in train_seasons:
        path = config.data_dir / f"{season}" / "features.parquet"
        df = load_parquet(path)
        if df is None:
            click.echo(
                f"No features found for {season}. Run 'build {season}' first."
            )
            sys.exit(1)
        all_features.append(df)

    features = pd.concat(all_features, ignore_index=True)
    click.echo(
        f"Training on {len(features)} games from {len(train_seasons)} seasons"
    )

    train_model(features, model_path=model_path)
    click.echo(f"Model saved to {model_path}")


@cli.command()
@click.argument("season", type=int)
@click.option(
    "--model-name", default="xgb_model.pkl", help="Model filename"
)
@click.pass_context
def evaluate(ctx: click.Context, season: int, model_name: str) -> None:
    """Evaluate model predictions on a season.

    Example: charliehustle evaluate 2024
    """
    from charliehustle.data.storage import load_parquet
    from charliehustle.models.evaluate import evaluate_predictions, print_evaluation
    from charliehustle.models.predict import predict_games
    from charliehustle.models.train import load_model

    config = ctx.obj["config"]
    model_path = config.data_dir / "models" / model_name

    model = load_model(model_path)

    path = config.data_dir / f"{season}" / "features.parquet"
    features = load_parquet(path)
    if features is None:
        click.echo(
            f"No features found for {season}. Run 'build {season}' first."
        )
        sys.exit(1)

    games = predict_games(model, features)
    metrics = evaluate_predictions(games)
    print_evaluation(metrics)


@cli.command()
@click.argument("season", type=int)
@click.option(
    "--model-name", default="xgb_model.pkl", help="Model filename"
)
@click.option(
    "--bankroll", type=float, default=1000.0, help="Starting bankroll"
)
@click.option(
    "--kelly-fraction",
    type=float,
    default=0.25,
    help="Kelly fraction (0-1)",
)
@click.option(
    "--min-edge",
    type=float,
    default=0.02,
    help="Minimum edge to place a bet",
)
@click.option(
    "--plot/--no-plot", default=True, help="Generate bankroll plot"
)
@click.pass_context
def simulate(
    ctx: click.Context,
    season: int,
    model_name: str,
    bankroll: float,
    kelly_fraction: float,
    min_edge: float,
    plot: bool,
) -> None:
    """Run a betting simulation on a season.

    Example: charliehustle simulate 2024 --bankroll 1000 --kelly-fraction 0.25
    """
    from charliehustle.betting.simulate import backtest
    from charliehustle.data.storage import load_parquet
    from charliehustle.models.predict import predict_games
    from charliehustle.models.train import load_model
    from charliehustle.viz import plot_bankroll

    config = ctx.obj["config"]
    config.initial_bankroll = bankroll
    config.kelly_fraction = kelly_fraction
    config.min_edge = min_edge

    model_path = config.data_dir / "models" / model_name
    model = load_model(model_path)

    path = config.data_dir / f"{season}" / "features.parquet"
    features = load_parquet(path)
    if features is None:
        click.echo(
            f"No features found for {season}. Run 'build {season}' first."
        )
        sys.exit(1)

    games = predict_games(model, features)
    results = backtest(games, config)

    if plot and len(results) > 0:
        plot_path = config.data_dir / "plots" / f"bankroll_{season}.png"
        plot_bankroll(
            results,
            title=f"{season} MLB Season Simulation",
            output_path=plot_path,
        )
