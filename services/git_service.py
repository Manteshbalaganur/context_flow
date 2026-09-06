from utils.helpers import now_iso,new_id
def collect_git(project,checkpoint_id):
    base={"available":False,"branch":"—","latest_commit":"No repository connected","commits":[],"warnings":[],"changed_files":[]}
    if not project.repository_path: base["warnings"].append("No local repository path is mapped to this project."); return base,[]
    try:
        from git import Repo
        repo=Repo(project.repository_path,search_parent_directories=True); changed=[]
        for item in repo.index.diff(None):
            kind={"A":"Added","M":"Modified","D":"Deleted","R":"Renamed"}.get(item.change_type,"Modified"); path=item.b_path or item.a_path
            changed.append({"change_id":new_id("chg"),"project_id":project.project_id,"checkpoint_id":checkpoint_id,"timestamp":now_iso(),"file_path":path,"change_type":kind,"insertions":0,"deletions":0,"diff_summary":f"{kind} working-tree file"})
        for path in repo.untracked_files: changed.append({"change_id":new_id("chg"),"project_id":project.project_id,"checkpoint_id":checkpoint_id,"timestamp":now_iso(),"file_path":path,"change_type":"Untracked","insertions":0,"deletions":0,"diff_summary":"New untracked file"})
        commits=[{"hash":c.hexsha[:7],"message":c.message.splitlines()[0],"author":c.author.name,"timestamp":c.committed_datetime.isoformat()} for c in list(repo.iter_commits(max_count=8))]
        return {"available":True,"branch":repo.active_branch.name if not repo.head.is_detached else "detached","latest_commit":commits[0]["message"] if commits else "No commits","commits":commits,"changed_files":changed,"warnings":[]},changed
    except Exception as exc: base["warnings"].append(f"Git collection unavailable: {exc}"); return base,[]
