from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Mock GitHub API")


class LabelsPayload(BaseModel):
    labels: list[str]


class CommentPayload(BaseModel):
    body: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


DATA = {
    "acme/roadrunner": {
        "issues": [
            {
                "number": 1,
                "title": "bug: crash on startup",
                "body": "App crashes on launch",
                "labels": [],
                "comments": [],
                "state": "open",
            },
            {
                "number": 2,
                "title": "How to configure webhook?",
                "body": "question about setup",
                "labels": [],
                "comments": [],
                "state": "open",
            },
            {
                "number": 3,
                "title": "UI unclear"
                ,"body": "need more details",
                "labels": [],
                "comments": [],
                "state": "open",
            },
        ]
    }
}


def _find_issue(repo: str, number: int) -> dict:
    for issue in DATA.get(repo, {}).get("issues", []):
        if issue["number"] == number:
            return issue
    raise HTTPException(status_code=404, detail="issue not found")


@app.get("/repos/{owner}/{repo}/issues")
def list_issues(owner: str, repo: str, state: str = "open") -> list[dict]:
    key = f"{owner}/{repo}"
    issues = DATA.get(key, {}).get("issues", [])
    return [issue for issue in issues if issue.get("state") == state]


@app.post("/repos/{owner}/{repo}/issues/{number}/labels")
def add_labels(owner: str, repo: str, number: int, payload: LabelsPayload) -> list[str]:
    key = f"{owner}/{repo}"
    issue = _find_issue(key, number)
    issue["labels"] = sorted(set(issue.get("labels", []) + payload.labels))
    return issue["labels"]


@app.post("/repos/{owner}/{repo}/issues/{number}/comments")
def create_comment(owner: str, repo: str, number: int, payload: CommentPayload) -> dict:
    key = f"{owner}/{repo}"
    issue = _find_issue(key, number)
    comment = {"id": len(issue["comments"]) + 1, "body": payload.body}
    issue["comments"].append(comment)
    return comment
