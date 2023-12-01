from linkedin_api import Linkedin
from linkedin_api.utils.helpers import get_id_from_urn, get_urn_from_raw_update


class CustomLinkedin(Linkedin):
    def __init__(self, username, password):
        super().__init__(username, password)

    def search(self, params, limit=-1, offset=0):
        """
        Custom LinkedIn search. Yield results as they are fetched.

        :param params: Search parameters (see code)
        :type params: dict
        :param limit: Maximum length of the returned list, defaults to -1 (no limit)
        :type limit: int, optional
        :param offset: Index to start searching from
        :type offset: int, optional

        :rtype: Iterator[dict]
        """
        max_count = Linkedin._MAX_SEARCH_COUNT
        count = 0

        while True:
            # when we're close to the limit, only fetch what we need to
            if limit > -1 and limit - count < max_count:
                max_count = limit - count
            default_params = {
                "count": str(max_count),
                "filters": "List()",
                "origin": "GLOBAL_SEARCH_HEADER",
                "q": "all",
                "start": count + offset,
                "queryContext": "List(spellCorrectionEnabled->true,relatedSearchesEnabled->true,kcardTypes->PROFILE|COMPANY)",
            }
            default_params.update(params)

            keywords = (
                f"keywords:{default_params['keywords']},"
                if "keywords" in default_params
                else ""
            )

            res = self._fetch(
                f"/graphql?variables=(start:{default_params['start']},origin:{default_params['origin']},"
                f"query:("
                f"{keywords}"
                f"flagshipSearchIntent:SEARCH_SRP,"
                f"queryParameters:{default_params['filters']},"
                f"includeFiltersInResponse:false))&=&queryId=voyagerSearchDashClusters"
                f".b0928897b71bd00a5a7291755dcd64f0"
            )
            data = res.json()

            data_clusters = data.get("data", []).get("searchDashClustersByAll", [])

            if not data_clusters:
                return []

            if (
                not data_clusters.get("_type", [])
                    == "com.linkedin.restli.common.CollectionResponse"
            ):
                return []

            for it in data_clusters.get("elements", []):
                if (
                    not it.get("_type", [])
                        == "com.linkedin.voyager.dash.search.SearchClusterViewModel"
                ):
                    continue

                for el in it.get("items", []):
                    if (
                        not el.get("_type", [])
                            == "com.linkedin.voyager.dash.search.SearchItem"
                    ):
                        continue

                    e = el.get("item", []).get("entityResult", [])
                    if not e:
                        continue
                    if (
                        not e.get("_type", [])
                            == "com.linkedin.voyager.dash.search.EntityResultViewModel"
                    ):
                        continue
                    count += 1
                    yield e

            # break the loop if we're done searching
            if (
                    (-1 < limit <= count)  # if our results exceed set limit
                    or count / max_count >= Linkedin._MAX_REPEATED_REQUESTS
            ) or count == 0:
                break

            self.logger.debug(f"results grew to {count}")

    def search_people(
            self,
            keywords=None,
            connection_of=None,
            network_depths=None,
            current_company=None,
            past_companies=None,
            nonprofit_interests=None,
            profile_languages=None,
            regions=None,
            industries=None,
            schools=None,
            contact_interests=None,
            service_categories=None,
            include_private_profiles=False,  # profiles without a public id, "LinkedIn Member"
            # Keywords filter
            keyword_first_name=None,
            keyword_last_name=None,
            # `keyword_title` and `title` are the same. We kept `title` for backward compatibility. Please only use one of them.
            keyword_title=None,
            keyword_company=None,
            keyword_school=None,
            network_depth=None,  # DEPRECATED - use network_depths
            title=None,  # DEPRECATED - use keyword_title
            **kwargs,
    ):
        """Perform a LinkedIn search for people.

        :param keywords: Keywords to search on
        :type keywords: str, optional
        :param current_company: A list of company URN IDs (str)
        :type current_company: list, optional
        :param past_companies: A list of company URN IDs (str)
        :type past_companies: list, optional
        :param nonprofit_interests: A list containing of nonprofit interest URN IDs (str)
        :type nonprofit_interests: list, optional
        :param regions: A list of geo URN IDs (str)
        :type regions: list, optional
        :param industries: A list of industry URN IDs (str)
        :type industries: list, optional
        :param schools: A list of school URN IDs (str)
        :type schools: list, optional
        :param profile_languages: A list of 2-letter language codes (str)
        :type profile_languages: list, optional
        :param contact_interests: A list containing one or both of "proBono" and "boardMember"
        :type contact_interests: list, optional
        :param service_categories: A list of service category URN IDs (str)
        :type service_categories: list, optional
        :param network_depth: Deprecated, use `network_depths`. One of "F", "S" and "O" (first, second and third+ respectively)
        :type network_depth: str, optional
        :param network_depths: A list containing one or many of "F", "S" and "O" (first, second and third+ respectively)
        :type network_depths: list, optional
        :param include_private_profiles: Include private profiles in search results. If False, only public profiles are included. Defaults to False
        :type include_private_profiles: boolean, optional
        :param keyword_first_name: First name
        :type keyword_first_name: str, optional
        :param keyword_last_name: Last name
        :type keyword_last_name: str, optional
        :param keyword_title: Job title
        :type keyword_title: str, optional
        :param keyword_company: Company name
        :type keyword_company: str, optional
        :param keyword_school: School name
        :type keyword_school: str, optional
        :param connection_of: Connection of LinkedIn user, given by profile URN ID
        :type connection_of: str, optional
        :param title: Job title (DEPRECATED - use keyword_title)
        :type title: str, optional

        :return: List of profiles (minimal data only)
        :rtype: list
        """
        filters = ["(key:resultType,value:List(PEOPLE))"]
        if connection_of:
            filters.append(f"(key:connectionOf,value:List({connection_of}))")
        if network_depths:
            stringify = " | ".join(network_depths)
            filters.append(f"(key:network,value:List({stringify}))")
        elif network_depth:
            filters.append(f"(key:network,value:List({network_depth}))")
        if regions:
            stringify = " | ".join(regions)
            filters.append(f"(key:geoUrn,value:List({stringify}))")
        if industries:
            stringify = " | ".join(industries)
            filters.append(f"(key:industry,value:List({stringify}))")
        if current_company:
            stringify = " | ".join(current_company)
            filters.append(f"(key:currentCompany,value:List({stringify}))")
        if past_companies:
            stringify = " | ".join(past_companies)
            filters.append(f"(key:pastCompany,value:List({stringify}))")
        if profile_languages:
            stringify = " | ".join(profile_languages)
            filters.append(f"(key:profileLanguage,value:List({stringify}))")
        if nonprofit_interests:
            stringify = " | ".join(nonprofit_interests)
            filters.append(f"(key:nonprofitInterest,value:List({stringify}))")
        if schools:
            stringify = " | ".join(schools)
            filters.append(f"(key:schools,value:List({stringify}))")
        if service_categories:
            stringify = " | ".join(service_categories)
            filters.append(f"(key:serviceCategory,value:List({stringify}))")
        # `Keywords` filter
        keyword_title = keyword_title if keyword_title else title
        if keyword_first_name:
            filters.append(f"(key:firstName,value:List({keyword_first_name}))")
        if keyword_last_name:
            filters.append(f"(key:lastName,value:List({keyword_last_name}))")
        if keyword_title:
            filters.append(f"(key:title,value:List({keyword_title}))")
        if keyword_company:
            filters.append(f"(key:company,value:List({keyword_company}))")
        if keyword_school:
            filters.append(f"(key:school,value:List({keyword_school}))")

        params = {"filters": "List({})".format(",".join(filters))}

        if keywords:
            params["keywords"] = keywords

        data = self.search(params, **kwargs)

        for item in data:
            if (
                not include_private_profiles
                and (item.get("entityCustomTrackingInfo") or {}).get(
                    "memberDistance", None
                )
                    == "OUT_OF_NETWORK"
            ):
                continue

            urn_id = get_id_from_urn(get_urn_from_raw_update(item.get("entityUrn", None)))
            distance = (item.get("entityCustomTrackingInfo") or {}).get("memberDistance", None)
            yield {
                "public_id": self.urn_to_public_id(urn_id),
                "distance": int(distance.split("_")[1]) if distance else None,
                "jobtitle": (item.get("primarySubtitle") or {}).get("text", None),
                "location": (item.get("secondarySubtitle") or {}).get("text", None),
                "name": (item.get("title") or {}).get("text", None),
            }

    def urn_to_public_id(self, urn_id):
        """Convert a LinkedIn URN ID to a public ID.

        :param urn_id: LinkedIn URN ID
        :type urn_id: str

        :return: Public ID
        :rtype: str
        """
        uri = f"/identity/profiles/{urn_id}/profileView"
        return self._fetch(uri).json()['profile']['miniProfile']['publicIdentifier']
